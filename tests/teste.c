#define V_SIZE 10
void teste_vetor(float*, int);

void teste_vetor(float vetor[], int scale) {
  for (int i = 0; i < V_SIZE; ++i) {
    vetor[i] += scale;
  }
}
