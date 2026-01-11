import { useState, useEffect } from 'react';
// @ts-ignore
import html2pdf from 'html2pdf.js';

interface ReportEditorProps {
  initialText: string;
}

export default function ReportEditor({ initialText }: ReportEditorProps) {
  const [text, setText] = useState("");

  useEffect(() => {
    setText(initialText);
  }, [initialText]);

  const handleDownloadPDF = () => {
    // 1. Create a temporary container for the PDF content
    const element = document.createElement('div');
    
    // 2. Format the raw text into nice HTML for the PDF
    // We replace your text markers with HTML tags
    const formattedHtml = text
      .split('\n')
      .map(line => {
        return `<p>${line}</p>`;
      })
      .join('');

    element.innerHTML = `<div style="padding: 20px; font-family: 'Arial', sans-serif;">${formattedHtml}</div>`;

    // 3. PDF Configuration
    const opt = {
      margin:       10,
      filename:     'Astrology_Report.pdf',
      image:        { type: "jpeg", quality: 0.98 },
      html2canvas:  { scale: 2 }, // Higher scale = better text clarity
      jsPDF:        { unit: 'mm', format: 'a4', orientation: 'portrait' }
    };

    // 4. Generate and Save
    html2pdf().set(opt).from(element).save();
  };

  return (
    <div className="w-full max-w-4xl mx-auto mt-6 bg-white shadow-lg rounded-lg overflow-hidden border border-gray-200">
      
      {/* Toolbar */}
      <div className="bg-gray-100 px-4 py-2 border-b border-gray-200 flex justify-between items-center">
        <h3 className="font-semibold text-gray-700">Report Editor</h3>
        <button 
          onClick={handleDownloadPDF}
          className="bg-red-600 text-white px-4 py-1.5 rounded text-sm hover:bg-red-700 transition flex items-center gap-2"
        >
          {/* PDF Icon SVG */}
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path></svg>
          Download PDF
        </button>
      </div>

      {/* Editable Area */}
      <textarea
        value={text}
        onChange={(e) => setText(e.target.value)}
        className="w-full h-screen p-8 text-gray-800 font-mono text-sm leading-relaxed focus:outline-none resize-y"
        style={{ minHeight: '600px', whiteSpace: 'pre-wrap' }} 
      />
    </div>
  );
}