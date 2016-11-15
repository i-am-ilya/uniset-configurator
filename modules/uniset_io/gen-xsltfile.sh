#!/bin/sh

[ -z "$1" ] && echo "Unknonwn template file" && exit 1
[ -z "$2" ] && echo "Unknonwn output filename" && exit 1

srcfile="$1"
destfile="$2"

# BASE_IO
PARAMS="no_iotestlamp range aref safety breaklim default ioignore ioinvert"

# Calibrations
PARAMS="$PARAMS cdiagram cmin cmax rmin rmax precision noprecision"

# Delay`s
PARAMS="$PARAMS ondelay offdelay jardelay"

# Filters
PARAMS="$PARAMS nofilter median leatsqr filterIIR filterT average"

# Thresholds
PARAMS="$PARAMS hilimit lowlimit threshold_aid threshold_invert"


DATA=

for p in ${PARAMS}; do
	DATA="${DATA}\n<xsl:call-template name=\"ifDefined\"><xsl:with-param name=\"value\"><xsl:value-of select=\"@${p}\"/></xsl:with-param><xsl:with-param name=\"varname\">${p}</xsl:with-param></xsl:call-template>"
done

cp -f ${srcfile} ${destfile}
subst "s|@PARAMS@|${DATA}|g" ${destfile}
