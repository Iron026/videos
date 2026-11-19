/* DTW em faixa (Sakoe-Chiba) entre duas sequências de vetores (n×d e m×d), distância cosseno.
   Passos (1,1), (1,0), (0,1). Devolve o caminho (pares i,j) do fim para o início. Compilado e chamado via ctypes
   por voz/comparar_narracao.py. Memória: n × (2w+1) floats. */
#include <stdlib.h>
#include <math.h>
#include <float.h>

int dtw_faixa(const float *a, int n, const float *b, int m, int d, int w, int *pi, int *pj) {
    int L = 2 * w + 1;
    float *D = (float *)malloc((size_t)n * L * sizeof(float));
    if (!D) return -1;
    for (size_t k = 0; k < (size_t)n * L; k++) D[k] = FLT_MAX;
    for (int i = 0; i < n; i++) {
        int c = (int)((double)i * (m - 1) / (n - 1 > 0 ? n - 1 : 1));
        for (int k = 0; k < L; k++) {
            int j = c - w + k; if (j < 0 || j >= m) continue;
            const float *x = a + (size_t)i * d, *y = b + (size_t)j * d; float s = 0;
            for (int q = 0; q < d; q++) s += x[q] * y[q];
            float custo = 1.0f - s, melhor = FLT_MAX;
            if (i == 0 && j == 0) melhor = 0;
            if (i > 0) {   /* vizinhos na linha anterior: (i-1, j) e (i-1, j-1) */
                int cp = (int)((double)(i - 1) * (m - 1) / (n - 1 > 0 ? n - 1 : 1));
                int k1 = j - (cp - w), k2 = j - 1 - (cp - w);
                if (k1 >= 0 && k1 < L && D[(size_t)(i - 1) * L + k1] < melhor) melhor = D[(size_t)(i - 1) * L + k1];
                if (k2 >= 0 && k2 < L && D[(size_t)(i - 1) * L + k2] < melhor) melhor = D[(size_t)(i - 1) * L + k2];
            }
            if (k > 0 && D[(size_t)i * L + k - 1] < melhor) melhor = D[(size_t)i * L + k - 1];   /* (i, j-1) */
            D[(size_t)i * L + k] = (melhor == FLT_MAX) ? FLT_MAX : melhor + custo;
        }
    }
    /* volta do fim (n-1, m-1) ao início */
    int i = n - 1, j = m - 1, t = 0;
    while (1) {
        pi[t] = i; pj[t] = j; t++;
        if (i == 0 && j == 0) break;
        int c = (int)((double)i * (m - 1) / (n - 1 > 0 ? n - 1 : 1));
        float v1 = FLT_MAX, v2 = FLT_MAX, v3 = FLT_MAX;
        if (i > 0) { int cp = (int)((double)(i - 1) * (m - 1) / (n - 1 > 0 ? n - 1 : 1));
            int k1 = j - 1 - (cp - w), k2 = j - (cp - w);
            if (j > 0 && k1 >= 0 && k1 < L) v1 = D[(size_t)(i - 1) * L + k1];
            if (k2 >= 0 && k2 < L) v2 = D[(size_t)(i - 1) * L + k2]; }
        { int k3 = j - 1 - (c - w); if (j > 0 && k3 >= 0 && k3 < L) v3 = D[(size_t)i * L + k3]; }
        if (v1 <= v2 && v1 <= v3) { i--; j--; } else if (v2 <= v3) { i--; } else { j--; }
        if (i < 0 || j < 0) break;
    }
    free(D);
    return t;
}
