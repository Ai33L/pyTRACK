
/* constraint file */

#include "file_path.h"

#define  CONSDAT         getenv("CONSDAT")
#define  CONSDAT_SMOOPY  getenv("CONSDAT_SMOOPY")
#define  CONSDAT_SPHERY  getenv("CONSDAT_SPHERY")


/* structure for constraint data used in the contrained conjugate
   gradient method of Goldfarb. (See gdfp_optimize.c)              */

struct cnst {
      double *nn;     /* normalized linearly independent constraint vectors */
      double *bb;     /* rhs of constraint divided by normalization factor */
      int numc;      /* total number of constraints */
      int numeq;     /* number of equality constraints */
};

/* equality constraints stored in the first numeq*dim elements of nn */

