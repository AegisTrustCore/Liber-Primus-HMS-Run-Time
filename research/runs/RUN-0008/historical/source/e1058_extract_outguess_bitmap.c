#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <jpeglib.h>

static void die(const char *m){perror(m); exit(1);} 

int main(int argc,char **argv){
 if(argc!=3){fprintf(stderr,"usage: %s in.jpg out.bitmap\n",argv[0]);return 2;}
 FILE *in=fopen(argv[1],"rb"); if(!in)die("fopen input");
 struct jpeg_decompress_struct cinfo; struct jpeg_error_mgr jerr;
 cinfo.err=jpeg_std_error(&jerr); jpeg_create_decompress(&cinfo); jpeg_stdio_src(&cinfo,in);
 if(jpeg_read_header(&cinfo,TRUE)!=JPEG_HEADER_OK){fprintf(stderr,"bad jpeg\n");return 1;}
 jvirt_barray_ptr *coef_arrays=jpeg_read_coefficients(&cinfo);
 fprintf(stderr,"image %ux%u comps=%d maxhs=%d maxvs=%d MCUs_per_row=%u total_iMCU_rows=%u progressive=%d\n",
    cinfo.image_width,cinfo.image_height,cinfo.num_components,cinfo.max_h_samp_factor,cinfo.max_v_samp_factor,
    cinfo.MCUs_per_row,cinfo.total_iMCU_rows,cinfo.progressive_mode);
 for(int ci=0;ci<cinfo.num_components;ci++){
   jpeg_component_info *cp=&cinfo.comp_info[ci];
   fprintf(stderr,"comp%d id=%d hs=%d vs=%d width_blocks=%u height_blocks=%u MCU_blocks=%d\n",ci,cp->component_id,cp->h_samp_factor,cp->v_samp_factor,cp->width_in_blocks,cp->height_in_blocks,cp->MCU_blocks);
 }
 size_t cap=1024*1024, nbits=0; unsigned char *bits=calloc(cap,1); if(!bits)die("calloc");
 #define ADD_BIT(b) do { if(nbits/8>=cap){size_t old=cap;cap*=2;bits=realloc(bits,cap);if(!bits)die("realloc");memset(bits+old,0,cap-old);} if(b) bits[nbits/8]|=(1u<<(nbits&7)); nbits++; } while(0)
 // Baseline interleaved entropy traversal: MCU row, MCU col, scan components, each component's v/h blocks.
 for(JDIMENSION my=0; my<cinfo.total_iMCU_rows; my++){
   for(JDIMENSION mx=0; mx<cinfo.MCUs_per_row; mx++){
     for(int ci=0;ci<cinfo.num_components;ci++){
       jpeg_component_info *cp=&cinfo.comp_info[ci];
       for(int v=0;v<cp->v_samp_factor;v++){
         JDIMENSION br=my*cp->v_samp_factor+v;
         if(br>=cp->height_in_blocks) continue;
         JBLOCKARRAY row=(*cinfo.mem->access_virt_barray)((j_common_ptr)&cinfo,coef_arrays[ci],br,1,FALSE);
         for(int h=0;h<cp->h_samp_factor;h++){
           JDIMENSION bc=mx*cp->h_samp_factor+h;
           if(bc>=cp->width_in_blocks) continue;
           JCOEFPTR block=row[0][bc];
           for(int k=0;k<DCTSIZE2;k++){
             int temp=(int)block[k];
             // OutGuess excludes only coefficient values 0 and +1; it includes -1.
             if(temp==0 || temp==1) continue;
             ADD_BIT(((uint16_t)temp)&1u);
           }
         }
       }
     }
   }
 }
 FILE *out=fopen(argv[2],"wb"); if(!out)die("fopen output");
 uint32_t be=((nbits&0xff)<<24)|((nbits&0xff00)<<8)|((nbits&0xff0000)>>8)|((nbits>>24)&0xff); // not used: write native metadata separately
 fwrite(bits,1,(nbits+7)/8,out); fclose(out);
 fprintf(stderr,"usable bits=%zu bytes=%zu\n",nbits,(nbits+7)/8);
 char meta[1024]; snprintf(meta,sizeof(meta),"%s.meta",argv[2]); FILE *mf=fopen(meta,"w"); if(mf){fprintf(mf,"%zu\n",nbits);fclose(mf);} 
 free(bits); jpeg_finish_decompress(&cinfo); jpeg_destroy_decompress(&cinfo); fclose(in); return 0;
}
