#include <assert.h>
#include "../native/indicator_state.h"

int main(void) {
  int hidden=0;
  assert(indicator_set_hidden(&hidden,0)==0);
  assert(hidden==0);
  assert(indicator_set_hidden(&hidden,1)==1);
  assert(hidden==1);
  assert(indicator_set_hidden(&hidden,1)==0);
  assert(indicator_set_hidden(&hidden,0)==1);
  assert(hidden==0);

  assert(indicator_needs_present(0,0)==0);
  assert(indicator_needs_present(1,0)==1);
  assert(indicator_needs_present(1,1)==0);
  return 0;
}
