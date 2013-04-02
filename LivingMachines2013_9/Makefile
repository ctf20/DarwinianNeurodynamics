WEBOTS          = ../../../..

OSTYPE         ?= $(shell uname)

ifeq ($(OSTYPE),linux)
OSTYPE          = Linux
endif

ifeq ($(OSTYPE),msys)
OSTYPE          = Windows
endif

ifneq ($(findstring MINGW, $(OSTYPE)),)
OSTYPE          = Windows
endif

INTERFACE       = controller.i
SWIG            = swig
SWIG_OPTS       = -c++ -python -outdir $(WEBOTS)/lib/python/
WEBOTS_INCLUDES = -I"$(WEBOTS)/include/controller/cpp" -I"$(WEBOTS)/include/controller/c"
WRAPPER         = $(INTERFACE:.i=_wrap.cpp)
WRAPPER_OBJECT  = $(WRAPPER:.cpp=.o)
PYOUT           = $(addprefix $(WEBOTS)/lib/python/,$(INTERFACE:.i=.py))
PYTHON_VERSION ?= 2.7
PYTHON_HOME_WINDOWS ?= /c/Python27

ifeq ($(OSTYPE),Windows)
C_FLAGS         = -c -O -Wall
LD_FLAGS        = -shared -Wl,--enable-auto-import
LIBS            = -L"$(WEBOTS)/lib" -L$(PYTHON_HOME_WINDOWS)/libs -lController -lCppController -lpython$(subst .,,$(PYTHON_VERSION))
LIBOUT          = $(addprefix $(WEBOTS)/lib/python/_,$(INTERFACE:.i=.pyd))
DEF             = _controller.def
PYTHON_INCLUDES = -I$(PYTHON_HOME_WINDOWS)/include
LIBCONTROLLER   = $(WEBOTS)/lib/Controller.dll
LIBCPPCONTROLLER= $(WEBOTS)/lib/CppController.dll
endif

ifeq ($(OSTYPE),Darwin)
C_FLAGS         = -c -Wall -fPIC
LD_FLAGS        = -dynamiclib -install_name _$(INTERFACE:.i=.dylib) -compatibility_version 1.0 -current_version 1.0.0
LIBS            = -L"$(WEBOTS)/lib" -lController -lCppController -lpython$(PYTHON_VERSION)
LIBOUT          = $(addprefix $(WEBOTS)/lib/python/_,$(INTERFACE:.i=.so))
PYTHON_INCLUDES = -I"/usr/include/python$(PYTHON_VERSION)"
LIBCONTROLLER   = $(WEBOTS)/lib/libController.dylib
LIBCPPCONTROLLER= $(WEBOTS)/lib/libCppController.dylib
endif

ifeq ($(OSTYPE),Linux)
C_FLAGS         = -c -Wall -fPIC -Wno-unused-but-set-variable
LD_FLAGS        = -shared
LIBS            = -L"$(WEBOTS)/lib" -lController -lCppController
LIBOUT          = $(addprefix $(WEBOTS)/lib/python/_,$(INTERFACE:.i=.so))
PYTHON_INCLUDES = -I"/usr/include/python$(PYTHON_VERSION)"
LIBCONTROLLER   = $(WEBOTS)/lib/libController.so
LIBCPPCONTROLLER= $(WEBOTS)/lib/libCppController.so
endif

ifeq ($(OSTYPE),Darwin)
SWIG_TEST = $(shell swig -version 2>&1 | cat)
ifeq ($(findstring not found,$(SWIG_TEST)),)
SWIG_EXISTS = $(shell which $(SWIG))
endif
else
SWIG_EXISTS     = $(shell which $(SWIG))
endif
TARGET          = $(PYOUT) $(LIBOUT)

build:$(TARGET)

$(PYOUT) $(WRAPPER):$(INTERFACE) $(LIBCONTROLLER) $(LIBCPPCONTROLLER)
ifneq ($(SWIG_EXISTS),)
	$(SWIG) $(SWIG_OPTS) $(WEBOTS_INCLUDES) -o $(WRAPPER) $< 
else
ifneq ($(MAKECMDGOALS),build)
	@echo "SWIG not installed."
endif
endif

$(LIBOUT):$(WRAPPER_OBJECT) $(LIBCONTROLLER) $(LIBCPPCONTROLLER)
	$(CXX) $(LD_FLAGS) $< $(DEF) $(LIBS) -o $@

$(LIBCONTROLLER):
	@echo "$(LIBCONTROLLER) doesn't exist"

$(LIBCPPCONTROLLER):
	@echo "$(LIBCPPCONTROLLER) doesn't exist"

$(WRAPPER_OBJECT):$(WRAPPER)
	$(CXX) $(C_FLAGS) $(WEBOTS_INCLUDES) $(PYTHON_INCLUDES) $< -o $@
	
clean:
	rm -f $(LIBOUT) $(WRAPPER_OBJECT) $(PYOUT:.py=.pyc) $(PYOUT) $(WRAPPER)

