import axios from 'axios';
import { useState, useEffect } from 'react';
import toast from 'react-hot-toast';
import MDEditor from '@uiw/react-md-editor';


export interface ReportEditorProps {
  kundliImageSrc: string;
  dashaContent: string | null;
  gocharImageSrc: string;
  reportContent: string | null;
}

const toBase64 = async (input: string) => {

  const response = await fetch(input);
  const img_blob = await response.blob();

  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onloadend = () => resolve(reader.result);
    reader.onerror = reject;
    reader.readAsDataURL(img_blob);
  });
};

const ReportEditor = ({ kundliImageSrc, dashaContent, gocharImageSrc, reportContent }: ReportEditorProps) => {
  const [editableReport, setEditableReport] = useState<string>("");

  useEffect(() => {
    if (reportContent)
      setEditableReport(reportContent);
  }, [reportContent]);



  const handleDownload = async () => {
    const [kundliBase64, gocharBase64] = await Promise.all([
      toBase64(kundliImageSrc),
      toBase64(gocharImageSrc)
    ]);

    const payload = {
      kundli_img: kundliBase64,
      gochar_img: gocharBase64,
      dasha_str: dashaContent,
      report_str: editableReport
    };

    const { data } = await axios.post('/api/download-pdf', payload, {
      headers: {
        'Content-Type': 'application/json',
      },
    });
    if (data.status == "error")
      toast.error('PDF generation Failed, try again!');
    else
      toast.success(`PDF generated at ${data.destination}`);


  }
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
          <div className="text-sm text-slate-600 leading-relaxed whitespace-pre-line">
            {dashaContent}
          </div>
        </div>

        <div>
          <h3 className="text-sm font-semibold uppercase tracking-wide text-slate-500 mb-2">
            Analysis (फलित विश्लेषण)
          </h3>
          <MDEditor
            value={editableReport}
            preview="edit"
            onChange={(val) => setEditableReport(val || "")}
            height={600}
          />
        </div>
        <button onClick={handleDownload} className="bg-indigo-900/95 hover:bg-indigo-800/95 text-white px-7 py-2.5 rounded-lg font-medium shadow-sm hover:shadow-md transition-shadow">
          Download PDF
        </button>
      </div>
    </div>
  );
};

export default ReportEditor;