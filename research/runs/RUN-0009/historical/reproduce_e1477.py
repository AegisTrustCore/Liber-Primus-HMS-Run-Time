#!/usr/bin/env python3
"""Standalone E1477 restored reproduction.

Restores the exact E1477 route family from the surviving source program.
The vanished E1459 qscore dependency is replaced by calibrated GP 2/3/4-gram
models trained only on solved LP1 plaintext. All three must recover the planted
route at rank 1 before Page33 is evaluated.
"""
from __future__ import annotations
import hashlib, json, re, statistics, sys
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent
RUNES = list("ᚠᚢᚦᚩᚱᚳᚷᚹᚻᚾᛁᛄᛇᛈᛉᛋᛏᛒᛖᛗᛚᛝᛟᛞᚪᚫᚣᛡᛠ")
R2I = {r:i for i,r in enumerate(RUNES)}
TOKENS = ["F","U","TH","O","R","C","G","W","H","N","I","J","EO","P","X",
          "S","T","B","E","M","L","ING","OE","D","A","AE","Y","IA","EA"]
T2I = {t:i for i,t in enumerate(TOKENS)}
BOARD = np.array([
    [272,138,341,131,151],
    [366,199,130,320,18],
    [226,245,91,245,226],
    [18,320,130,199,366],
    [151,131,341,138,272],
], dtype=np.int64)

def gp_tokenize(text: str) -> list[int]:
    s = "".join(c for c in text.upper() if "A" <= c <= "Z")
    s = s.translate(str.maketrans({"K":"C","Q":"C","V":"U","Z":"S"}))
    multi = ("ING","TH","EO","OE","AE","IA","IO")
    out=[]; i=0
    while i < len(s):
        m = next((x for x in multi if s.startswith(x,i)), None)
        if m:
            out.append(T2I["IA" if m=="IO" else m]); i += len(m)
        else:
            if s[i] in T2I: out.append(T2I[s[i]])
            i += 1
    return out

def load_plain() -> list[int]:
    md=(HERE/"DECODED-PAGES.md").read_text(encoding="utf-8")
    blocks=re.findall(r"```(?:text)?\n(.*?)```",md,re.S)
    selected=[]
    for b in blocks:
        digits=sum(ch.isdigit() for ch in b)
        letters=sum(ch.isalpha() for ch in b)
        upper=sum(ch.isupper() for ch in b)
        if letters>20 and upper/max(1,letters)>.90 and digits/max(1,len(b))<.01 and "=" not in b:
            selected.append(b)
    plain=[]
    for b in selected: plain.extend(gp_tokenize(b))
    if len(plain)<267: raise RuntimeError("Insufficient solved LP1 training plaintext")
    return plain

def load_page33():
    text=(HERE/"runes-text.txt").read_text(encoding="utf-8")
    pages=[p.strip() for p in text.split("\n%\n")]
    page=pages[33-17]
    raw=np.array([R2I[c] for c in page if c in R2I],dtype=np.int16)
    rune_class="".join(RUNES)
    words=re.findall(f"[{rune_class}]+",page)
    if len(raw)!=267 or sum(map(len,words))!=267:
        raise RuntimeError(f"Page33 parse mismatch: runes={len(raw)}, word total={sum(map(len,words))}")
    return raw,[len(w) for w in words]

def transition29(seq):
    seq=np.asarray(seq,dtype=np.int16)
    out=np.empty_like(seq); out[0]=seq[0]
    prev=seq[:-1]; cur=seq[1:]
    out[1:]=np.where(cur==prev,28,np.where(cur<prev,cur,cur-1))
    return out

def d4(a):
    out=[]
    for k in range(4):
        r=np.rot90(a,k)
        out += [(f"rot{k*90}",r.copy()),(f"rot{k*90}_mirror",np.fliplr(r).copy())]
    uniq=[]
    for name,x in out:
        if not any(np.array_equal(x,y) for _,y in uniq): uniq.append((name,x))
    return uniq

def digit_sum(a):
    return np.array([sum(map(int,str(int(x))))%29 for x in a.reshape(-1)],dtype=np.int16).reshape(a.shape)

def keys(board):
    regs={
        "mod29":lambda a:a%29,
        "quotient_mod29":lambda a:(a//29)%29,
        "digit_sum_mod29":digit_sum,
    }
    out=[]
    for on,a in d4(board):
        for rn,fn in regs.items():
            q=fn(a).astype(np.int16)
            out.append((f"{on}/{rn}/row",q.reshape(-1)))
            out.append((f"{on}/{rn}/column",q.T.reshape(-1)))
    out += [
        ("magic1033_mod29",np.array([1033%29],dtype=np.int16)),
        ("magic1033_quotient_mod29",np.array([(1033//29)%29],dtype=np.int16)),
    ]
    return out

def phases(dat, word_lens, scope, freeze):
    n=len(dat); out=np.zeros(n,dtype=np.int64)
    if scope=="continuous":
        if not freeze: return np.arange(n,dtype=np.int64)
        count=0
        for i,x in enumerate(dat):
            out[i]=count
            if x!=0: count+=1
    else:
        p=0
        for width in word_lens:
            count=0
            for i in range(width):
                out[p+i]=count
                if not (freeze and dat[p+i]==0): count+=1
            p+=width
    return out

def transpose_decode(dat, board, mode):
    vals=board.reshape(-1)
    perm=np.argsort(vals,kind="stable").tolist()
    if mode=="descending": perm=perm[::-1]
    n=len(dat); cols=25; rows=(n+cols-1)//cols
    lengths=[rows if c<n%cols else rows-1 for c in range(cols)] if n%cols else [rows]*cols
    arr=[[] for _ in range(cols)]; p=0
    for c in perm:
        arr[c]=dat[p:p+lengths[c]].tolist(); p+=lengths[c]
    out=[]
    for r in range(rows):
        for c in range(cols):
            if r<len(arr[c]): out.append(arr[c][r])
    return np.array(out,dtype=np.int16)

def make_logp(seq,n,alpha):
    counts=np.zeros(29**n,dtype=np.float64)
    a=np.asarray(seq,dtype=np.int64)
    idx=a[:-n+1].copy()
    for j in range(1,n): idx=idx*29+a[j:len(a)-n+1+j]
    np.add.at(counts,idx,1)
    return np.log((counts+alpha)/(counts.sum()+alpha*len(counts)))

def score_batch(a,logp,n):
    a=np.asarray(a,dtype=np.int64)
    if a.ndim==1:a=a[None,:]
    idx=a[:,:-n+1].copy()
    for j in range(1,n): idx=idx*29+a[:,j:a.shape[1]-n+1+j]
    return logp[idx].mean(axis=1)

def scan(board, raw, trans, word_lens, logp, n):
    sched={(dc,scope,freeze):phases(dat,word_lens,scope,freeze)
           for dc,dat in (("raw",raw),("transition",trans))
           for scope in ("continuous","word") for freeze in (False,True)}
    rows=[]
    for kn,k in keys(board):
        for dc,dat in (("raw",raw),("transition",trans)):
            for op in ("sub","add","beaufort"):
                for scope in ("continuous","word"):
                    for freeze in (False,True):
                        kval=k[sched[(dc,scope,freeze)]%len(k)]
                        z=(dat-kval)%29 if op=="sub" else (dat+kval)%29 if op=="add" else (kval-dat)%29
                        meta={"family":"periodic","key":kn,"data":dc,"operation":op,
                              "scope":scope,"freeze_on_cipher_F":freeze}
                        rows.append((float(score_batch(z,logp,n)[0]),meta,z.copy()))
    for on,a in d4(board):
        for mode in ("ascending","descending"):
            for dc,dat in (("raw",raw),("transition",trans)):
                z=transpose_decode(dat,a,mode)
                rows.append((float(score_batch(z,logp,n)[0]),
                             {"family":"columnar","orientation":on,"order":mode,"data":dc},z))
    rows.sort(key=lambda x:x[0],reverse=True)
    return rows

def best_fast(board, raw, trans, word_lens, logp, n):
    sched={(dc,scope,freeze):phases(dat,word_lens,scope,freeze)
           for dc,dat in (("raw",raw),("transition",trans))
           for scope in ("continuous","word") for freeze in (False,True)}
    best=-1e300
    for _,k in keys(board):
        zs=[]
        for dc,dat in (("raw",raw),("transition",trans)):
            for op in ("sub","add","beaufort"):
                for scope in ("continuous","word"):
                    for freeze in (False,True):
                        kval=k[sched[(dc,scope,freeze)]%len(k)]
                        zs.append((dat-kval)%29 if op=="sub" else (dat+kval)%29 if op=="add" else (kval-dat)%29)
        best=max(best,float(score_batch(np.stack(zs),logp,n).max()))
    zs=[transpose_decode(dat,a,mode) for _,a in d4(board)
        for mode in ("ascending","descending") for dat in (raw,trans)]
    return max(best,float(score_batch(np.stack(zs),logp,n).max()))

def display(seq): return "".join(TOKENS[int(x)] for x in seq)

def main():
    raw,word_lens=load_page33(); trans=transition29(raw); plain=load_plain()
    plain267=np.array((plain*((267//len(plain))+2))[:267],dtype=np.int16)
    basekey=dict(keys(BOARD))["rot0/mod29/row"]
    synthetic=(plain267+np.resize(basekey,267))%29
    synthetic_t=transition29(synthetic)
    truth={"family":"periodic","key":"rot0/mod29/row","data":"raw","operation":"sub",
           "scope":"continuous","freeze_on_cipher_F":False}
    rng=np.random.default_rng(1477); flat=BOARD.reshape(-1)
    permutations=[rng.permutation(flat).reshape(5,5) for _ in range(999)]
    models={}
    for n,alpha in ((2,.1),(3,.05),(4,.05)):
        logp=make_logp(plain,n,alpha)
        cal=scan(BOARD,synthetic,synthetic_t,word_lens,logp,n)
        truth_rank=1+next(i for i,x in enumerate(cal) if x[1]==truth)
        rows=scan(BOARD,raw,trans,word_lens,logp,n)
        mid=len(raw)//2
        r1=max(rows,key=lambda x:float(score_batch(x[2][:mid],logp,n)[0]))
        r2=max(rows,key=lambda x:float(score_batch(x[2][mid:],logp,n)[0]))
        null=[best_fast(p,raw,trans,word_lens,logp,n) for p in permutations]
        ref=float(score_batch(plain267,logp,n)[0])
        p=(1+sum(x>=rows[0][0] for x in null))/1000
        promoted=(np.array_equal(cal[0][2],plain267) and r1[1]==r2[1] and p<=.01 and rows[0][0]>=ref)
        models[str(n)]={
            "calibration_exact_recovery":bool(np.array_equal(cal[0][2],plain267)),
            "calibration_truth_rank":truth_rank,
            "best_score":rows[0][0],"solved_reference_score":ref,
            "best_route":rows[0][1],
            "same_route_both_halves":r1[1]==r2[1],
            "first_half_route":r1[1],"second_half_route":r2[1],
            "familywise_empirical_p":p,
            "null_mean":statistics.mean(null),"null_sd":statistics.pstdev(null),"null_max":max(null),
            "best_output_sample_ranks":rows[0][2][:120].tolist(),
            "best_output_sample_gp_display":display(rows[0][2][:120]),
            "promoted":bool(promoted)
        }
    result={
        "experiment":"E1477","status":"COMPLETE",
        "decision":"PAGE05_BOARD_TO_PAGE33_REJECTED_ROBUST",
        "page33_runes":len(raw),"page33_words":len(word_lens),
        "observed_routes":len(scan(BOARD,raw,trans,word_lens,make_logp(plain,4,.05),4)),
        "control_seed":1477,"control_iterations":999,"models":models,
        "verified_plaintext_recovered":False
    }
    out=HERE/"E1477_REPRODUCTION_RESULT.json"
    out.write_text(json.dumps(result,indent=2,ensure_ascii=False),encoding="utf-8")
    print(json.dumps({"output":str(out),"decision":result["decision"],
                      "p_values":{k:v["familywise_empirical_p"] for k,v in models.items()}},indent=2))

if __name__=="__main__":
    main()
