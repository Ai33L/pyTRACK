SOURCES=tr2nc.c \
       read_tracks.c \
       write_track_netcdf.c \
       new_time.c \
       julian.c


OBJECTS = $(SOURCES:.c=.o)

OBJECT=tr2nc.o read_tracks.o write_track_netcdf.o new_time.o julian.o

#CFLAGS = -g -Xa -xsb

CFLAGS = -g -fPIC -ansi -Wall -I../../include ${ADDINCS} -D${SYSTEM} -D${HAVNETC} $(AD_C_FLAGS) 

LIBS = -lm ${ADLIBS}


.KEEP_STATE:

.PHONY: all
all: $(OBJECTS)
	@echo "All object files built."

%.o: %.c
	$(CC) $(CFLAGS) -c $< -o $@