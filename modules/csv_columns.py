
columns = [
            # grouping information
            "TIME", "TASK","GROUP","GROUPING",
            # channels 
           "CH_R", "CH_P", "CH_Y", "CH_H", "CH_T",
           "ARMING","AUX2","AUX3",
           # floats & long values, used by tasks
           "float0","float1", "float2", "float3", "float4", "float5", "float6", "float7",
           "ldata0","ldata1","ldata2","ldata3","ldata4","ldata5","ldata6","ldata7",
           # pid values used by tasks
           "pidRoll","pidPitch","pidYaw","pidThrust","pidHover",
           # constants.....
           "HOVER_MINIMAL_HEIGHT", "HOVER_MIN_DISTANCE", "HOVER_MAX_DISTANCE",
           # CRC 16Bit, PODRacer send 8Bytes 0000+4BytesCRC
           "CRC"
           ];
