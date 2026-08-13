#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <errno.h>
#include <jpeglib.h>

static void die(const char *m){ perror(m); exit(1); }
static void put_u16le(FILE *f, uint16_t x){ unsigned char b[2]={(unsigned char)(x&255),(unsigned char)(x>>8)}; if(fwrite(b,1,2,f)!=2) die("write strata"); }

int main(int argc,char **argv){
  if(argc!=4){fprintf(stderr,"usage: %s in.jpg out.bitmap out.strata\n",argv[0]);return 2;}
  FILE *in=fopen(argv[1],"rb"); if(!in) die("fopen input");
  FILE *bout=fopen(argv[2],"wb"); if(!bout) die("fopen bitmap");
  FILE *sout=fopen(argv[3],"wb"); if(!sout) die("fopen strata");
  struct jpeg_decompress_struct cinfo; struct jpeg_error_mgr jerr;
  cinfo.err=jpeg_std_error(&jerr); jpeg_create_decompress(&cinfo); jpeg_stdio_src(&cinfo,in);
  if(jpeg_read_header(&cinfo,TRUE)!=JPEG_HEADER_OK){fprintf(stderr,"bad jpeg\n");return 1;}
  jvirt_barray_ptr *coef_arrays=jpeg_read_coefficients(&cinfo);
  size_t cap=1024*1024, nbits=0; unsigned char *bits=calloc(cap,1); if(!bits)die("calloc");
  uint64_t strata_counts[55296]; uint64_t strata_ones[55296];
  memset(strata_counts,0,sizeof(strata_counts)); memset(strata_ones,0,sizeof(strata_ones));
  #define ADD_BIT(b) do { if(nbits/8>=cap){size_t old=cap;cap*=2;bits=realloc(bits,cap);if(!bits)die("realloc");memset(bits+old,0,cap-old);} if(b) bits[nbits/8]|=(1u<<(nbits&7)); nbits++; } while(0)
  for(JDIMENSION my=0; my<cinfo.total_iMCU_rows; my++){
    for(JDIMENSION mx=0; mx<cinfo.MCUs_per_row; mx++){
      for(int ci=0;ci<cinfo.num_components;ci++){
        jpeg_component_info *cp=&cinfo.comp_info[ci];
        for(int v=0;v<cp->v_samp_factor;v++){
          JDIMENSION br=my*cp->v_samp_factor+v; if(br>=cp->height_in_blocks) continue;
          JBLOCKARRAY row=(*cinfo.mem->access_virt_barray)((j_common_ptr)&cinfo,coef_arrays[ci],br,1,FALSE);
          for(int h=0;h<cp->h_samp_factor;h++){
            JDIMENSION bc=mx*cp->h_samp_factor+h; if(bc>=cp->width_in_blocks) continue;
            int ry=(int)((3ULL*br)/cp->height_in_blocks); if(ry>2)ry=2;
            int rx=(int)((3ULL*bc)/cp->width_in_blocks); if(rx>2)rx=2;
            int region=ry*3+rx;
            JCOEFPTR block=row[0][bc];
            for(int k=0;k<DCTSIZE2;k++){
              int temp=(int)block[k]; if(temp==0 || temp==1) continue;
              int bit=((uint16_t)temp)&1u;
              int mag=temp<0?-temp:temp;
              int mb=(mag-1)/2; if(mb<0)mb=0; if(mb>31)mb=31;
              uint16_t sid=(uint16_t)((((ci*64+k)*9+region)*32)+mb);
              ADD_BIT(bit); put_u16le(sout,sid); strata_counts[sid]++; strata_ones[sid]+=bit;
            }
          }
        }
      }
    }
  }
  if(fwrite(bits,1,(nbits+7)/8,bout)!=(nbits+7)/8) die("write bitmap");
  fclose(bout); fclose(sout);
  char meta[4096]; snprintf(meta,sizeof(meta),"%s.meta",argv[2]); FILE *mf=fopen(meta,"w"); if(!mf)die("meta"); fprintf(mf,"%zu\n",nbits); fclose(mf);
  char csv[4096]; snprintf(csv,sizeof(csv),"%s.counts.csv",argv[3]); FILE *cf=fopen(csv,"w"); if(!cf)die("counts");
  fprintf(cf,"stratum_id,component,dct_index,region,magpair_bin,count,ones,odd_fraction\n");
  for(int sid=0;sid<55296;sid++) if(strata_counts[sid]){
    int x=sid; int mb=x%32; x/=32; int region=x%9; x/=9; int k=x%64; int ci=x/64;
    fprintf(cf,"%d,%d,%d,%d,%d,%llu,%llu,%.12g\n",sid,ci,k,region,mb,(unsigned long long)strata_counts[sid],(unsigned long long)strata_ones[sid],(double)strata_ones[sid]/strata_counts[sid]);
  }
  fclose(cf);
  fprintf(stderr,"usable_bits=%zu strata_nonempty=",nbits); int ne=0; for(int i=0;i<55296;i++)if(strata_counts[i])ne++; fprintf(stderr,"%d\n",ne);
  free(bits); jpeg_finish_decompress(&cinfo); jpeg_destroy_decompress(&cinfo); fclose(in); return 0;
}
