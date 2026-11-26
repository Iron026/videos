"""Rodada 11: confere cada salto fora dos cortes do definitivo na revisão 540 aprovada (mesmo quadro). Rodar em episodio/ com PYTHONPATH=../decupagem."""
import json, subprocess, numpy as np, sys
from PIL import Image
sys.path.insert(0,'.')
import os
# rodada 12 (opcionais; padrão = R11): SUF_VALIDACAO no nome dos registros lidos/gravados; FINAL_MP4 = definitivo a conferir
SUF=os.environ.get('SUF_VALIDACAO',''); FINAL=os.environ.get('FINAL_MP4','ep02_definitivo_1080x1920.mp4')
R=f'../relatorios/testes_r10/validacao_final_r11_video{SUF}.json'; r=json.load(open(R))
def ler(f,w=108,h=192):
    b=subprocess.run(['ffmpeg','-v','error','-i',f,'-vf',f'scale={w}:{h}:flags=area','-f','rawvideo','-pix_fmt','rgb24','-'],capture_output=True,check=True).stdout
    return np.frombuffer(b,np.uint8).reshape(-1,h,w,3).astype(np.float32).mean(3)
def gros(G): return np.stack([np.asarray(Image.fromarray(g.astype(np.uint8)).resize((32,56),Image.BILINEAR),np.float32) for g in G])
def corr(a,b):
    a=a-a.mean();b=b-b.mean();return float((a*b).sum()/(np.linalg.norm(a)*np.linalg.norm(b)+1e-9))
F=gros(ler(FINAL)); Rf=gros(ler('ep02_v11_revisao_referencia.mp4'))
import planos as PL
PLR=PL.resolvidos()['planos']
def plano(i):
    g=i/30; v=[p['id'] for p in PLR if p['t0']<=g<p['t1']]; return v
out=[]; nao=[]
for s in r['saltos']['fora_dos_cortes']:
    i=s['quadro']; cr,dr=corr(Rf[i],Rf[i-1]),float(np.abs(Rf[i]-Rf[i-1]).mean())
    mesmo = cr<0.93 and dr>6
    eq = abs(cr-s['corr'])<=0.05
    x=dict(**s,planos=plano(i),ref_corr=round(cr,3),ref_dif=round(dr,1),mesmo_salto_na_ref=mesmo, final_x_ref_quadro=round(corr(F[i],Rf[i]),3))
    out.append(x)
    if not mesmo: nao.append(x)
print('total fora',len(out),'iguais na ref',len(out)-len(nao),'sem par na ref',len(nao))
for x in nao: print(x)
# also: jumps present in ref but not in final (outside cuts)
json.dump(dict(fora_dos_cortes=out,sem_par_na_referencia=nao),open(f'../relatorios/testes_r10/validacao_final_r11_saltos_x_ref540{SUF}.json','w'),ensure_ascii=False,indent=1)
