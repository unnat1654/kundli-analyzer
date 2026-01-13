import { useState, useEffect } from 'react';
import { PDFDownloadLink } from '@react-pdf/renderer';
import { PDFCreator } from './PDFCreator'; // Import component from Step 2

export interface ReportEditorProps{
  kundliImageSrc: string;
  dashaContent: string;
  gocharImageSrc: string;
  reportContent: string;
}

const ReportEditor = ({kundliImageSrc,dashaContent,gocharImageSrc, reportContent}: ReportEditorProps) => {
  const [editableReport, setEditableReport]=useState<string>("");

  useEffect(()=>{
    setEditableReport(reportContent);
  },[reportContent]);
  return (
    <div className="grid md:grid-cols-2 gap-8">
    <div className="space-y-4">
      {kundliImageSrc && <img className="rounded-xl border" src={kundliImageSrc} />}
      {gocharImageSrc && <img className="rounded-xl border" src={gocharImageSrc} />}
    </div>

    <div className="space-y-4">
      <div className="text-sm text-slate-500">{dashaContent}</div>

      <textarea
        className="w-full h-64 border border-slate-300 rounded-lg p-4 focus:ring-2 focus:ring-indigo-500"
        value={editableReport}
        onChange={(e) => setEditableReport(e.target.value)}
      />

      <PDFDownloadLink
          document={
            <PDFCreator 
              kundliImageSrc={kundliImageSrc} 
              gocharImageSrc={gocharImageSrc} 
              dashaContent={dashaContent} 
              reportContent={editableReport} 
            />
          }
          fileName="final_report.pdf"
      >
        <button className="bg-teal-500 hover:bg-teal-600 text-white px-6 py-2 rounded-lg">
          Download PDF
        </button>
      </PDFDownloadLink>
    </div>
  </div>
  );
};

export default ReportEditor;