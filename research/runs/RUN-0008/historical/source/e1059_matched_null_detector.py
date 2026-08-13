#!/usr/bin/env python3
from __future__ import annotations
import argparse, csv, hashlib, importlib.util, json, math
from pathlib import Path
import numpy as np

PRINTABLE = np.zeros(256,dtype=np.uint8)
for x in list(range(32,127))+[9,10,13]: PRINTABLE[x]=1
PGP_PREFIX=b'-----BEGIN PGP SIGNED MESSAGE-----'
KNOWN_POS=set([0,1,2,3,4,8,10,11,12,13])
DEV_POS=KNOWN_POS-{8}
HELD_OUT={8}
FALSE_CONTROLS=set([17,18,20,21,22,43])

def load_independent(path:Path):
    spec=importlib.util.spec_from_file_location('independent',path)
    mod=importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
    return mod

def selected_positions(mod,total:int,seed:int,declared:int,nbytes:int=64):
    key=b'Default key'; sch=mod.PositionSchedule(key); pos=[]
    # Header: four bytes, LSB first.
    for _ in range(4):
        for _ in range(8):
            if sch.position>=total: raise EOFError
            pos.append(sch.position); sch.advance()
    sch.add_seed(seed)
    left=declared
    for _ in range(min(nbytes,declared)):
        sch.retune(total,left)
        for _ in range(8):
            if sch.position>=total: raise EOFError
            pos.append(sch.position); sch.advance()
        left-=1
    return np.asarray(pos,dtype=np.int64)

def encryption_keystream(mod,n:int)->np.ndarray:
    c=mod.StreamCipher(b'Encryption',b'Default key')
    return np.fromiter((c._next() for _ in range(n)),dtype=np.uint8,count=n)

def exact_stratified_parity_null(selected_sids:np.ndarray, counts:np.ndarray, ones:np.ndarray, reps:int, rng:np.random.Generator):
    mtotal=len(selected_sids)
    sim=np.empty((reps,mtotal),dtype=np.uint8)
    # Sorting avoids repeated np.where scans.
    order=np.argsort(selected_sids,kind='stable')
    sorted_sids=selected_sids[order]
    boundaries=np.flatnonzero(np.r_[True,sorted_sids[1:]!=sorted_sids[:-1],True])
    for a,b in zip(boundaries[:-1],boundaries[1:]):
        sid=int(sorted_sids[a]); cols=order[a:b]; m=b-a
        N=int(counts[sid]); K=int(ones[sid])
        if m>N: raise ValueError((sid,m,N))
        if K==0: sim[:,cols]=0; continue
        if K==N: sim[:,cols]=1; continue
        if m==1:
            sim[:,cols[0]]=(rng.random(reps)<(K/N)).astype(np.uint8)
            continue
        k=rng.hypergeometric(K,N-K,m,size=reps)
        u=rng.random((reps,m))
        # Uniform random k-subset in each row.
        rank=np.argsort(np.argsort(u,axis=1),axis=1)
        sim[:,cols]=(rank<k[:,None]).astype(np.uint8)
    return sim

def entropy(data:bytes)->float:
    if not data:return 0.0
    c=np.bincount(np.frombuffer(data,dtype=np.uint8),minlength=256)
    p=c[c>0]/len(data)
    return float(-(p*np.log2(p)).sum())

def prefix_suffix_runs(data:bytes,val=0xff):
    a=0
    while a<len(data) and data[a]==val:a+=1
    b=0
    while b<len(data) and data[len(data)-1-b]==val:b+=1
    return a,b

def coeff_stats(count_csv:Path):
    rows=[]
    with count_csv.open(newline='') as f:
        for r in csv.DictReader(f):
            r['component']=int(r['component']);r['count']=int(r['count']);r['ones']=int(r['ones']); rows.append(r)
    N=sum(r['count'] for r in rows); O=sum(r['ones'] for r in rows)
    chi=0.0;df=0;absdev=0.0
    comps={}
    for r in rows:
        n=r['count'];o=r['ones'];
        if n:
            chi += 4.0*(o-n/2.0)**2/n; df+=1; absdev += abs(o/n-.5)*n
            c=comps.setdefault(r['component'],[0,0]);c[0]+=n;c[1]+=o
    return {
      'eligible_coefficients':N,'odd_coefficients':O,'global_odd_fraction':O/N,
      'stratified_parity_chi2':chi,'stratified_parity_df':df,
      'stratified_parity_z':(chi-df)/math.sqrt(2*df) if df else None,
      'weighted_mean_abs_odd_deviation':absdev/N,
      'component_odd_fraction':{str(k):v[1]/v[0] for k,v in sorted(comps.items())}
    }

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--root',type=Path,required=True);ap.add_argument('--reps',type=int,default=8191);ap.add_argument('--body-bytes',type=int,default=64)
    a=ap.parse_args();root=a.root
    mod=load_independent(root/'src/e1059_independent_retrieve.py')
    ks=encryption_keystream(mod,a.body_bytes)
    results=[]
    for page in range(75):
        meta=json.load(open(root/'extracted'/f'page_{page:02d}.extraction.json'))
        bm_path=root/'coeffmeta'/f'{page:02d}.bitmap'; st_path=root/'coeffmeta'/f'{page:02d}.strata'
        packed=np.fromfile(bm_path,dtype=np.uint8)
        bits=np.unpackbits(packed,bitorder='little')[:meta['usable_bits']].astype(np.uint8,copy=False)
        sids=np.fromfile(st_path,dtype='<u2')
        if len(sids)!=meta['usable_bits']: raise ValueError((page,len(sids),meta['usable_bits']))
        maxsid=int(sids.max())
        counts=np.bincount(sids,minlength=maxsid+1)
        ones=np.bincount(sids,weights=bits,minlength=maxsid+1).astype(np.int64)
        pos=selected_positions(mod,meta['usable_bits'],meta['seed'],meta['declared_length'],a.body_bytes)
        obs_sel=bits[pos]
        # Verify extracted header/body against the exact ledger.
        weights=np.array([1,2,4,8,16,32,64,128],dtype=np.uint16)
        obs_raw_header=(obs_sel[:32].reshape(4,8)*weights).sum(axis=1).astype(np.uint8).tobytes()
        if obs_raw_header.hex()!=meta['raw_header_hex']: raise AssertionError((page,obs_raw_header.hex(),meta['raw_header_hex']))
        nbody=(len(obs_sel)-32)//8
        obs_raw_body=(obs_sel[32:].reshape(nbody,8)*weights).sum(axis=1).astype(np.uint8)
        out_file=next(iter(sorted((root/'extracted').glob(f'page_{page:02d}*.out'))))
        output=out_file.read_bytes()
        obs_decoded=obs_raw_body ^ ks[:nbody]
        if bytes(obs_decoded)!=output[:nbody]: raise AssertionError(('body',page))

        seed_rng=(0xE1059000 + page*1000003 + a.reps) & 0xffffffffffffffff
        rng=np.random.default_rng(seed_rng)
        sim=exact_stratified_parity_null(sids[pos],counts,ones,a.reps,rng)
        sim_header_zeros=32-sim[:,:32].sum(axis=1)
        sim_raw=(sim[:,32:].reshape(a.reps,nbody,8)*weights).sum(axis=2).astype(np.uint8)
        sim_dec=sim_raw ^ ks[:nbody][None,:]
        sim_print=PRINTABLE[sim_dec].sum(axis=1)
        prefix_len=min(len(PGP_PREFIX),nbody)
        sim_pgp=(sim_dec[:,:prefix_len]==np.frombuffer(PGP_PREFIX[:prefix_len],dtype=np.uint8)).all(axis=1) if prefix_len else np.zeros(a.reps,dtype=bool)

        obs_header_zeros=int(32-obs_sel[:32].sum())
        obs_print=int(PRINTABLE[obs_decoded].sum())
        obs_pgp=bool(bytes(obs_decoded).startswith(PGP_PREFIX))
        p_header=(1+int((sim_header_zeros>=obs_header_zeros).sum()))/(a.reps+1)
        p_print=(1+int((sim_print>=obs_print).sum()))/(a.reps+1)
        p_pgp=(1+int((sim_pgp>=obs_pgp).sum()))/(a.reps+1) if obs_pgp else 1.0
        tests=75*3
        fwer_header=min(1.0,p_header*tests);fwer_print=min(1.0,p_print*tests);fwer_pgp=min(1.0,p_pgp*tests)

        raw_file=next(iter(sorted((root/'extracted').glob(f'page_{page:02d}*.raw'))))
        raw=raw_file.read_bytes(); ffpre,ffsuf=prefix_suffix_runs(raw)
        print_frac=sum((32<=x<=126) or x in (9,10,13) for x in output)/len(output) if output else 0.0
        non_attractor=meta['raw_header_hex']!='ffffffff'
        significant=min(fwer_header,fwer_print,fwer_pgp)<=0.05
        detector_positive=bool(meta['complete'] and (non_attractor or significant))
        row={
          'page':page,'label':('known_positive' if page in KNOWN_POS else 'false_control' if page in FALSE_CONTROLS else 'unlabeled'),
          'development_positive':page in DEV_POS,'held_out_positive':page in HELD_OUT,
          **meta,
          'non_attractor_header':non_attractor,'dominant_header_family':meta['raw_header_hex']=='ffffffff',
          'raw_ff_prefix_bytes':ffpre,'raw_ff_suffix_bytes':ffsuf,
          'raw_entropy_bits_per_byte':entropy(raw),'output_entropy_bits_per_byte':entropy(output),
          'output_printable_fraction':print_frac,'output_prefix_hex':output[:32].hex(),
          'pgp_armor_signature':output.startswith(PGP_PREFIX),
          'null':{
             'schema':'exact parity permutation within component×DCT×region×adjacent-magnitude-pair strata',
             'repetitions':a.reps,'body_bytes_scored':nbody,'rng_seed':seed_rng,
             'observed_header_zero_count':obs_header_zeros,
             'observed_printable_count':obs_print,'observed_printable_fraction':obs_print/nbody if nbody else 0,
             'observed_pgp_prefix':obs_pgp,
             'empirical_p_header_zeros':p_header,'empirical_p_printable':p_print,'empirical_p_pgp_prefix':p_pgp,
             'bonferroni_tests':tests,
             'familywise_p_header_zeros':fwer_header,'familywise_p_printable':fwer_print,'familywise_p_pgp_prefix':fwer_pgp,
             'minimum_familywise_p':min(fwer_header,fwer_print,fwer_pgp)
          },
          'coefficient_parity':coeff_stats(root/'coeffmeta'/f'{page:02d}.strata.counts.csv'),
          'detector_positive':detector_positive,
          'detector_reason':(('complete + non-attractor header' + (' + familywise matched-null anomaly' if significant else '')) if detector_positive else
             'rejected: incomplete extraction' if not meta['complete'] else
             'rejected: dominant FFFFFFFF attractor header without familywise anomaly')
        }
        results.append(row)
        print(f"{page:02d} hdr={meta['raw_header_hex']} complete={int(meta['complete'])} pmin={row['null']['minimum_familywise_p']:.6g} det={int(detector_positive)}",flush=True)
    out={'schema':'HMS_E1059_MATCHED_NULL_DETECTOR_V1','frozen_repetitions':a.reps,'body_bytes_scored':a.body_bytes,
         'multiple_testing':'Bonferroni over 75 pages × 3 predeclared statistics',
         'detector_rule':'complete AND (non-FFFFFFFF header OR minimum familywise p <= 0.05)',
         'development_positives':sorted(DEV_POS),'held_out_positives':sorted(HELD_OUT),'false_controls':sorted(FALSE_CONTROLS),
         'pages':results}
    (root/'results'/'e1059_page_detector_ledger.json').write_text(json.dumps(out,indent=2))
    # Flattened CSV.
    fields=['page','label','development_positive','held_out_positive','raw_header_hex','decoded_header_hex','seed','declared_length','recovered_length','missing_bytes','complete','capacity_margin_bits','non_attractor_header','raw_ff_prefix_bytes','raw_ff_suffix_bytes','raw_entropy_bits_per_byte','output_entropy_bits_per_byte','output_printable_fraction','pgp_armor_signature','header_zero_count','printable_count_64','p_header','p_printable','p_pgp','fwer_p_header','fwer_p_printable','fwer_p_pgp','minimum_familywise_p','eligible_coefficients','global_odd_fraction','stratified_parity_z','weighted_mean_abs_odd_deviation','detector_positive','detector_reason','output_sha256']
    with (root/'results'/'e1059_page_detector_ledger.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields);w.writeheader()
        for r in results:
            n=r['null'];c=r['coefficient_parity']
            w.writerow({'page':r['page'],'label':r['label'],'development_positive':r['development_positive'],'held_out_positive':r['held_out_positive'],'raw_header_hex':r['raw_header_hex'],'decoded_header_hex':r['decoded_header_hex'],'seed':r['seed'],'declared_length':r['declared_length'],'recovered_length':r['recovered_length'],'missing_bytes':r['missing_bytes'],'complete':r['complete'],'capacity_margin_bits':r['capacity_margin_bits'],'non_attractor_header':r['non_attractor_header'],'raw_ff_prefix_bytes':r['raw_ff_prefix_bytes'],'raw_ff_suffix_bytes':r['raw_ff_suffix_bytes'],'raw_entropy_bits_per_byte':r['raw_entropy_bits_per_byte'],'output_entropy_bits_per_byte':r['output_entropy_bits_per_byte'],'output_printable_fraction':r['output_printable_fraction'],'pgp_armor_signature':r['pgp_armor_signature'],'header_zero_count':n['observed_header_zero_count'],'printable_count_64':n['observed_printable_count'],'p_header':n['empirical_p_header_zeros'],'p_printable':n['empirical_p_printable'],'p_pgp':n['empirical_p_pgp_prefix'],'fwer_p_header':n['familywise_p_header_zeros'],'fwer_p_printable':n['familywise_p_printable'],'fwer_p_pgp':n['familywise_p_pgp_prefix'],'minimum_familywise_p':n['minimum_familywise_p'],'eligible_coefficients':c['eligible_coefficients'],'global_odd_fraction':c['global_odd_fraction'],'stratified_parity_z':c['stratified_parity_z'],'weighted_mean_abs_odd_deviation':c['weighted_mean_abs_odd_deviation'],'detector_positive':r['detector_positive'],'detector_reason':r['detector_reason'],'output_sha256':r['output_sha256']})

if __name__=='__main__': main()
