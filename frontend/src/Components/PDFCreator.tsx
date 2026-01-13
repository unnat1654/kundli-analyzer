import { Page, Text, View, Document, StyleSheet, Image } from '@react-pdf/renderer';
import type { ReportEditorProps } from './ReportEditor';

// Define styles for the PDF (similar to CSS but specific to this library)
const styles = StyleSheet.create({
  page: {
    padding: 30,
    fontFamily: 'Helvetica',
  },
  header: {
    fontSize: 24,
    marginBottom: 20,
    textAlign: 'center',
    fontWeight: 'bold',
  },
  sectionHeading: {
    fontSize: 16,
    marginTop: 15,
    marginBottom: 10,
    color: '#333',
    fontWeight: 'bold',
    textDecoration: 'underline',
  },
  image: {
    width: 300,
    height: 300,
    alignSelf: 'center',
    marginBottom: 10,
  },
  textBlock: {
    fontSize: 12,
    lineHeight: 1.5,
    marginBottom: 10,
    textAlign: 'justify',
  },
});


export const PDFCreator = ({ kundliImageSrc, dashaContent, gocharImageSrc, reportContent }: ReportEditorProps) => (
  <Document>
    <Page size="A4" style={styles.page}>
      <Text style={styles.header}>My Report</Text>

      <View wrap={false}>
        <Text style={styles.sectionHeading}>Birth Chart</Text>
        {kundliImageSrc && <Image style={styles.image} src={kundliImageSrc} />}
      </View>

      <View>
        <Text style={styles.sectionHeading}>Dasha Information</Text>
        <Text style={styles.textBlock}>{dashaContent}</Text>
      </View>

      <View wrap={false}>
        <Text style={styles.sectionHeading}>Gochar Phal(Transit Chart)</Text>
        {gocharImageSrc && <Image style={styles.image} src={gocharImageSrc} />}
      </View>

      <View>
        <Text style={styles.sectionHeading}>Kundli Analysis</Text>
        <Text style={styles.textBlock}>{reportContent}</Text>
      </View>
    </Page>
  </Document>
);