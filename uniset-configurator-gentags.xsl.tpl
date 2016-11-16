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
<xsl:for-each select="//sensors/item">
<xsl:sort select="@id" order="ascending" data-type="text"/>
<xsl:sort select="@name" order="ascending" data-type="text"/>
<xsl:if test="normalize-space(@F_FIELD@)@F_RULE@'@F_VALUE@'">
@<xsl:value-of select="@name"/>@		<xsl:call-template name="parameters"/><xsl:text>
</xsl:text>
</xsl:if>
</xsl:for-each>
</xsl:template>

<xsl:template name="parameters">
@PARAMS@
</xsl:template>
</xsl:stylesheet>
