<?xml version='1.0' encoding="utf-8" ?>
<xsl:stylesheet  xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version='1.0'
	             xmlns:date="http://exslt.org/dates-and-times">

<xsl:output method="text" indent="yes" encoding="utf-8"/>

<xsl:template match="/">
<!-- "io","id","type"."card","subdev","channel","textname"  -->

<xsl:for-each select="//sensors/item">
<xsl:sort select="@io" order="ascending" data-type="text"/>
<xsl:sort select="@card" order="ascending" data-type="number"/>
<xsl:sort select="@subdev" order="ascending" data-type="number"/>
<xsl:sort select="@channel" order="ascending" data-type="number"/>
<xsl:if test="@io!=''">@<xsl:value-of select="@name"/>@		io="<xsl:value-of select="@io"/>" card="<xsl:value-of select="@card"/>" subdev="<xsl:value-of select="@subdev"/>" channel="<xsl:value-of select="@channel"/>"<xsl:text>
</xsl:text>
</xsl:if>
</xsl:for-each>

</xsl:template>
</xsl:stylesheet>
