<?xml version='1.0' encoding="utf-8" ?>
<xsl:stylesheet  xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version='1.0'
	             xmlns:date="http://exslt.org/dates-and-times">

<xsl:output method="text" indent="no" encoding="utf-8"/>
<xsl:strip-space elements="*"/>

<xsl:template name="ifDefined">
	<xsl:param name="varname"/>
	<xsl:param name="value"/>
	<xsl:if test="normalize-space($value)!=''"><xsl:text> </xsl:text><xsl:value-of select="$varname"/>="<xsl:value-of select="$value"/>"</xsl:if>
</xsl:template>

<xsl:template match="/">
<!-- "io","id","type"."card","subdev","channel","textname"  -->

<xsl:for-each select="//sensors/item">
<xsl:sort select="@io" order="ascending" data-type="text"/>
<xsl:sort select="@card" order="ascending" data-type="number"/>
<xsl:sort select="@subdev" order="ascending" data-type="number"/>
<xsl:sort select="@channel" order="ascending" data-type="number"/>
<xsl:if test="@io!=''">@<xsl:value-of select="@name"/>@		iotype="<xsl:value-of select="@iotype"/>" io="<xsl:value-of select="@io"/>" card="<xsl:value-of select="@card"/>" subdev="<xsl:value-of select="@subdev"/>" channel="<xsl:value-of select="@channel"/>"<xsl:call-template name="parameters"/></xsl:if><xsl:text>
</xsl:text>
</xsl:for-each>
</xsl:template>

<xsl:template name="parameters">
@PARAMS@
</xsl:template>
</xsl:stylesheet>
