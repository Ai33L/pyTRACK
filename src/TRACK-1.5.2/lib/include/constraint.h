
/* constraint file */

#include "file_path.h"

#define  CONSDAT         Addtwo(DATPATH,constraints.dat)
#define  CONSDAT_SMOOPY  Addtwo(DATPATH,constraints.dat.reg)
#define  CONSDAT_SPHERY  Addtwo(DATPATH,constraints.dat.sphery)


/* structure for constraint data used in the contrained conjugate
   gradient method of Goldfarb. (See gdfp_optimize.c)              */

struct cnst {
      double *nn;     /* normalized linearly independent constraint vectors */
      double *bb;     /* rhs of constraint divided by normalization factor */
      int numc;      /* total number of constraints */
      int numeq;     /* number of equality constraints */
};

/* equality constraints stored in the first numeq*dim elements of nn */

