#include <stdio.h>
#include <string.h>

#define MAX 100

void ler_string(char *s);

int main (int argc, char *argv[])
{
  char s[MAX];
  int a;
  scanf("%i", &a);
  ler_string(s);
  printf("%s %i", s, a);

  return 0;
}

void ler_string(char *s) {
  scanf("\n");
  fgets(s, MAX, stdin); 
  int s_len = strlen(s);
  if( s[s_len-1] == '\n' ) s[s_len-1] = '\0';
}
