import { useState, useEffect } from 'react';
import { PDFDownloadLink } from '@react-pdf/renderer';
import { PDFCreator } from './PDFCreator'; // Import component from Step 2

export interface ReportEditorProps {
  kundliImageSrc: string;
  dashaContent: string;
  gocharImageSrc: string;
  reportContent: string;
}

const ReportEditor = ({ kundliImageSrc, dashaContent, gocharImageSrc, reportContent }: ReportEditorProps) => {
  const [editableReport, setEditableReport] = useState<string>("");

  useEffect(() => {
    setEditableReport(reportContent);
  }, [reportContent]);
  return (
    <div className="grid md:grid-cols-2 gap-8">
      <div className="space-y-6">
        {kundliImageSrc && (
          <div>
            <h3 className="text-sm font-semibold uppercase tracking-wide text-slate-500 mb-2">
              Birth Chart (जन्म पत्रिका)
            </h3>
            <img className="rounded-xl" src={kundliImageSrc} />
          </div>
        )}

        {gocharImageSrc && (
          <div>
            <h3 className="text-sm font-semibold uppercase tracking-wide text-slate-500 mb-2">
              Transit Chart (गोचर फल)
            </h3>
            <img className="rounded-xl" src={gocharImageSrc} />
          </div>
        )}
      </div>

      <div className="space-y-6">
        <div>
          <h3 className="text-sm font-semibold uppercase tracking-wide text-slate-500 mb-2">
            Dasha (दशा)
          </h3>
          <div className="text-sm text-slate-600 leading-relaxed">
            {dashaContent}
          </div>
        </div>

        <div>
          <h3 className="text-sm font-semibold uppercase tracking-wide text-slate-500 mb-2">
            Analysis (फलित विश्लेषण)
          </h3>
          <textarea
            className="w-full h-96 border border-slate-300 rounded-lg p-4 focus:ring-1 focus:ring-indigo-400/30"
            value={editableReport}
            onChange={(e) => setEditableReport(e.target.value)}
          />
        </div>

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
          <button className="bg-indigo-900/95 hover:bg-indigo-800/95 text-white px-7 py-2.5 rounded-lg font-medium shadow-sm hover:shadow-md transition-shadow">
            Download PDF
          </button>
        </PDFDownloadLink>
      </div>
    </div>
  );
};

export default ReportEditor;