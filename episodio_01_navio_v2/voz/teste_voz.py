"""Teste de voz ElevenLabs — Will - Deep (CstacWqMhJQlnfLPxRG4). NÃO executado: aguarda autorização/chave.

A chave NUNCA vai para o repositório. Duas formas de fornecê-la:
  1) credencial salva no ambiente da sessão (o proxy injeta o cabeçalho xi-api-key em api.elevenlabs.io);
  2) variável de ambiente ELEVENLABS_API_KEY no momento da execução.

Uso: python3 voz/teste_voz.py            → gera voz/amostra_will_deep.mp3 e voz/amostra_will_deep.json
Gasta 204 caracteres (créditos, × multiplicador da voz se houver) do plano da conta. Registra créditos antes/depois.
"""
import json, os, sys, time, urllib.request

VOZ = 'CstacWqMhJQlnfLPxRG4'
MODELO = 'eleven_multilingual_v2'
AJUSTES = dict(stability=0.50, similarity_boost=0.75, style=0.0, use_speaker_boost=True, speed=1.0)
# Trecho do roteiro aprovado (sem alterações) + assinatura, para conferir a pronúncia do nome do canal.
TEXTO = ("Se eu jogar este bloco de aço na água, ele afunda. Mas e se eu usar toneladas do mesmo aço para construir um navio? "
         "Parece impossível. Então vamos montar um. "
         "De Olho no Invisível. O invisível ganha forma.")
AQUI = os.path.dirname(os.path.abspath(__file__))
CHAVE = os.environ.get('ELEVENLABS_API_KEY', 'injetada-pelo-proxy')


def req(metodo, caminho, corpo=None, aceitar='application/json'):
    r = urllib.request.Request('https://api.elevenlabs.io' + caminho, method=metodo,
                               data=json.dumps(corpo).encode() if corpo else None,
                               headers={'xi-api-key': CHAVE, 'Content-Type': 'application/json', 'Accept': aceitar})
    with urllib.request.urlopen(r, timeout=120) as resp:
        return resp.read()


def main():
    info = {}
    assin = json.loads(req('GET', '/v1/user/subscription'))
    info['plano'] = assin.get('tier'); info['caracteres_antes'] = assin.get('character_count')
    info['licenca_comercial'] = info['plano'] not in (None, 'free')
    voz = json.loads(req('GET', f'/v1/voices/{VOZ}'))
    info['voz'] = {k: voz.get(k) for k in ('voice_id', 'name', 'category', 'labels', 'description', 'high_quality_base_model_ids')}
    sh = voz.get('sharing') or {}
    info['voz']['biblioteca'] = {k: sh.get(k) for k in ('notice_period', 'free_users_allowed', 'live_moderation_enabled', 'rate', 'disable_at_unix')}
    t = time.time()
    audio = req('POST', f'/v1/text-to-speech/{VOZ}?output_format=mp3_44100_192',
                dict(text=TEXTO, model_id=MODELO, language_code='pt', voice_settings=AJUSTES), aceitar='audio/mpeg')
    saida = os.path.join(AQUI, 'amostra_will_deep.mp3'); open(saida, 'wb').write(audio)
    assin2 = json.loads(req('GET', '/v1/user/subscription'))
    info.update(modelo=MODELO, voice_id=VOZ, ajustes=AJUSTES, texto=TEXTO, caracteres_texto=len(TEXTO),
                caracteres_depois=assin2.get('character_count'), tempo_s=round(time.time() - t, 1), arquivo=saida)
    info['creditos_consumidos'] = (info['caracteres_depois'] or 0) - (info['caracteres_antes'] or 0)
    try:
        import subprocess
        d = subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', saida], capture_output=True, text=True).stdout
        info['duracao_s'] = round(float(d), 2)
    except Exception: pass
    json.dump(info, open(os.path.join(AQUI, 'amostra_will_deep.json'), 'w'), ensure_ascii=False, indent=1)
    print(json.dumps(info, ensure_ascii=False, indent=1))
    if not info['licenca_comercial']:
        print('ATENÇÃO: plano gratuito — o áudio NÃO pode ser usado comercialmente (exige atribuição).', file=sys.stderr)


if __name__ == '__main__':
    main()
