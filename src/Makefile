# ===== Configuration =====

TARBALL := TRACK-1.5.2.tar.bz2
SRC_DIR := TRACK-1.5.2
LIBNAME := libtrack.so
LIBUTILSNAME := libtrackutils.so

# Tools
CC := gcc
FC := gfortran

# Exported environment
export CC
export FC
export ARFLAGS :=
export PATH := $(PATH):.

# ===== Default target =====

.PHONY: all
all: libtrack

# ===== Build shared library =====

.PHONY: libtrack
libtrack: $(LIBNAME)

$(LIBNAME): untar build_objects
	@echo "Linking shared library $(LIBNAME)"
	cd $(SRC_DIR) && \
	gfortran -shared -fPIC -o $(LIBNAME) \
	    src/*.o \
	    lib/src/*.o \
	    lib/FFT/*.o \
	    lib/chisqr.src/*.o \
	    -lnetcdf
	cd $(SRC_DIR) && \
	gfortran -shared -fPIC -o $(LIBUTILSNAME) \
	    utils/PYWRAPPED/*.o \
	    -lnetcdf
	cp $(SRC_DIR)/$(LIBNAME) .
	cp $(SRC_DIR)/$(LIBUTILSNAME) .

# ===== Untar legacy source =====

.PHONY: untar
untar:
	@if [ ! -d "$(SRC_DIR)" ]; then \
	    echo "Extracting $(TARBALL)"; \
	    tar -xjf $(TARBALL); \
	else \
	    echo "$(SRC_DIR) already exists, skipping untar"; \
	fi

# ===== Run master build =====

.PHONY: build_objects
build_objects:
	cd $(SRC_DIR) && \
	master -build -i=linux -f=linux
	cd $(SRC_DIR) && \
	make utils

# ===== Clean =====

.PHONY: clean
clean:
	rm -f $(LIBNAME)
	rm -rf $(SRC_DIR)

