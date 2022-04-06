LDFLAGS += -L${KAYA_VISION_POINT_LIB_PATH}
LDFLAGS += -Wl,-rpath,${KAYA_VISION_POINT_LIB_PATH}
LDFLAGS += -Wl,-rpath,'$$ORIGIN'
KYFLAGS+=-lz #only needed when KYFGLib is built with $KAYA_ATTR_OPENCV_LINK_MODE == "local"

all: cyclic_buffers queued_buffers chameleon startup

cyclic_buffers: KYFGLib_Example.c
	gcc -o KYFGLib_Example KYFGLib_Example.c -I$(KAYA_VISION_POINT_INCLUDE_PATH) $(LDFLAGS) -lKYFGLib $(KYFLAGS)

queued_buffers: KYFGLib_Example_QueuedBuffers.c
	gcc -o KYFGLib_Example_QueuedBuffers KYFGLib_Example_QueuedBuffers.c -I$(KAYA_VISION_POINT_INCLUDE_PATH) $(LDFLAGS) -lKYFGLib $(KYFLAGS)

chameleon: KY_Chameleon_Example.c
	gcc -o KY_Chameleon_Example KY_Chameleon_Example.c -I$(KAYA_VISION_POINT_INCLUDE_PATH) $(LDFLAGS) -lKYFGLib $(KYFLAGS)
	
startup: KAYA_SystemStartup.c
	gcc -o KAYA_SystemStartup KAYA_SystemStartup.c -I$(KAYA_VISION_POINT_INCLUDE_PATH) $(LDFLAGS) -lKYFGLib $(KYFLAGS)
