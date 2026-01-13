import { useState} from 'react';
import './App.css';
import MapSelector from "./Components/MapSelector.tsx";
import type { LatLng } from './Interfaces.tsx';
import { CreatableMultiSelect, type Option } from './Components/CreatableMultiSelect.tsx';
import { defaultJyotishSchools, defaultRemedyCategories } from './config.tsx';
import axios from 'axios';
import ReportEditor from './Components/ReportEditor.tsx';

function App() {
  const [day, setDay] = useState<string>("");
  const [month, setMonth] = useState<string>("");
  const [year, setYear] = useState<string>("");
  const [hours, setHours] = useState<string>("");
  const [minutes, setMinutes] = useState<string>("");
  const [latitude, setLatitude] = useState<number>(28.6139);
  const [longitude, setLongitude] = useState<number>(77.2090);

  const [incRemedyCategories, setIncRemedyCategories] = useState<readonly Option[]>([]);
  const [excRemedyCategories, setExcRemedyCategories] = useState<readonly Option[]>([]);
  const [jyotishSchools, setJyotishSchools] = useState<readonly Option[]>([]);

  const [language, setLanguage]=useState<string>("");

  const [loading, setLoading]=useState<boolean>(false);

  const [kundliImageSrc,setKundliImageSrc]=useState<string | null>("1");
  const [dashaContent, setDashaContent]=useState<string>("1");
  const [gocharImageSrc,setGocharImageSrc]=useState<string | null>("dd");
  const [reportContent, setReportContent]=useState<string>("1");

  const isFormInvalid = !year || !month || !day || !hours || !minutes || !latitude || !longitude || loading;
  const hasOverlap = incRemedyCategories.some(a =>
    excRemedyCategories.some(b => a.value === b.value)
  );

  const handleNumberInput = (
    value: string, 
    setter: (val: string) => void, 
    min: number, 
    max: number
  ) => {
    if (value === "") {
      setter(value);
      return;
    }

    const numValue = parseInt(value, 10);
    
    if (!isNaN(numValue) && numValue >= min && numValue <= max) {
      setter(value);
    }
  };

  const handleYearInput = (val: string) => {
    if (val === "") {
        setYear(val);
        return;
    }
    const num = parseInt(val, 10);
    if (!isNaN(num) && num >= 0 && val.length <= 4) {
        setYear(val);
    }
  };

  const handleLocationUpdate = (location: LatLng) => {
    setLatitude(location.lat);
    setLongitude(location.lng);
  };

  const handleGenerateReport = async () => {
    // Basic Client-side check before sending
    if (isFormInvalid) {
      alert("Please fill in all date and time fields!");
      return;
    }
    if (hasOverlap) {
      alert("Remedy Inclusions and Exclusions have a common value!");
      return;
    }

    const birth_details={
      year: parseInt(year, 10),
      month: parseInt(month, 10),
      day: parseInt(day, 10),
      hours: parseInt(hours, 10),
      minutes: parseInt(minutes, 10),
      latitude: Number(latitude),
      longitude: Number(longitude),
    };
    
    const analysis_payload = {
      ...birth_details,
      jyotish_schools: jyotishSchools.map(opt => opt.value),
      inc_remedy_categories: incRemedyCategories.map(opt => opt.value),
      exc_remedy_categories: excRemedyCategories.map(opt => opt.value),
      language: language
    };

    try {
      setLoading(true);
      const kundliResponse = await axios.post('http://localhost:5000/generate-kundli', birth_details, {responseType:'blob'});
      setKundliImageSrc(URL.createObjectURL(kundliResponse.data));

      const gocharResponse = await axios.post('http://localhost:5000/generate-gochar', birth_details, {responseType:'blob'});
      setGocharImageSrc(URL.createObjectURL(gocharResponse.data));

      const analysisResponse = await axios.post('http://localhost:5000/generate-prompt', analysis_payload);
      console.log("Report Generated:", analysisResponse.data);

      setReportContent(analysisResponse.data.analysis_result);
      setDashaContent(analysisResponse.data.dasha);
      setLoading(false);
      alert("Report Request Sent!");
    } catch (error) {
      console.error("Error generating report:", error);
      alert("Failed to generate report.");
    }
  };

  return (
     <div className="min-h-screen bg-gradient-to-br from-slate-50 via-white to-indigo-100/40 text-slate-700">
    <div className="max-w-7xl mx-auto px-6 py-12 space-y-12">

      {/* Header */}
      <header className="space-y-2">
        <h1 className="text-4xl font-semibold tracking-tight text-slate-900">
          Astro Report Studio
        </h1>
        <p className="text-slate-500 max-w-xl">
          Generate, refine and export beautifully structured astrological reports.
        </p>
      </header>

      {/* Card */}
      <div className="bg-white/80 backdrop-blur border border-slate-200/70 shadow-[0_8px_30px_-12px_rgba(0,0,0,0.08)] p-8 space-y-10">

        {/* Date & Time */}
        <section className="space-y-6">
          <h2 className="text-lg font-medium text-slate-900 border-l-2 border-indigo-300/60 pl-3">Birth Details</h2>

          <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
            {[
              { v: day, set: setDay, min: 1, max: 31, label: "Day" },
              { v: month, set: setMonth, min: 1, max: 12, label: "Month" },
              { v: year, set: handleYearInput, label: "Year", type: "year" },
              { v: hours, set: setHours, min: 0, max: 23, label: "Hours" },
              { v: minutes, set: setMinutes, min: 0, max: 59, label: "Minutes" },
            ].map((f, i) => (
              <div key={i} className="space-y-1">
                <label className="text-xs tracking-wide uppercase text-slate-400 pl-[2px]">{f.label}</label>
                <input
                  type="number"
                  value={f.v}
                  onChange={(e) =>
                    f.type === "year"
                      ? handleYearInput(e.target.value)
                      : handleNumberInput(e.target.value, f.set as any, f.min!, f.max!)
                  }
                  className="w-full rounded-lg border border-slate-300 px-3 py-2 hover:border-indigo-300 focus:outline-none focus:ring-1 focus:ring-indigo-400/30 focus:border-indigo-400"
                />
              </div>
            ))}
          </div>
        </section>

        {/* Location */}
        <section className="space-y-4">
          <h2 className="text-lg font-medium text-slate-900 border-l-2 border-indigo-300/60 pl-3">Birth Location</h2>
          <div className="rounded-xl overflow-hidden border border-slate-200 bg-slate-50 ring-1 ring-indigo-100">
            <MapSelector onLocationSelect={handleLocationUpdate} />
          </div>
        </section>

        {/* Preferences */}
        <section className="grid md:grid-cols-3 gap-6">
          <div>
            <label className="text-xs tracking-wide uppercase text-slate-400 pl-[2px]">Include Remedies</label>
            <CreatableMultiSelect
              value={incRemedyCategories}
              onChange={setIncRemedyCategories}
              placeholder="Select categories"
              defaultOptions={defaultRemedyCategories}
            />
          </div>

          <div>
            <label className="text-xs tracking-wide uppercase text-slate-400 pl-[2px]">Exclude Remedies</label>
            <CreatableMultiSelect
              value={excRemedyCategories}
              onChange={setExcRemedyCategories}
              placeholder="Select categories"
              defaultOptions={defaultRemedyCategories}
            />
          </div>

          <div>
            <label className="text-xs tracking-wide uppercase text-slate-400 pl-[2px]">Jyotish Schools</label>
            <CreatableMultiSelect
              value={jyotishSchools}
              onChange={setJyotishSchools}
              placeholder="Select schools"
              defaultOptions={defaultJyotishSchools}
            />
          </div>
        </section>

        {/* Language */}
        <section className="max-w-sm">
          <label className="text-xs tracking-wide uppercase text-slate-400 pl-[2px]">Specify Language</label>
          <input
            value={language}
            onChange={(e) => setLanguage(e.target.value)}
            className="w-full rounded-lg border border-slate-300 px-3 py-2  hover:border-indigo-300 focus:outline-none focus:ring-1 focus:ring-indigo-400/30 focus:border-indigo-400"
            placeholder="English, Hindi..."
          />
        </section>

        {/* Generate Button */}
        <div className="pt-6 border-t border-slate-200">
          <button
            onClick={handleGenerateReport}
            disabled={(isFormInvalid || hasOverlap)}
            className="bg-indigo-600 hover:bg-indigo-700 disabled:bg-slate-300 text-white px-8 py-3 rounded-xl font-medium transition"
          >
            {loading ? "Generating..." : "Generate Report"}
          </button>
        </div>
      </div>

      {/* Report */}
      <section className="space-y-6">
        <h2 className="text-lg font-medium text-slate-900 border-l-2 border-indigo-300/60 pl-3">Report</h2>
        {kundliImageSrc && gocharImageSrc && reportContent && dashaContent && (
          <div className="bg-white border border-slate-200 rounded-xl p-6">
            <ReportEditor
              kundliImageSrc={kundliImageSrc}
              dashaContent={dashaContent}
              gocharImageSrc={gocharImageSrc}
              reportContent={reportContent}
            />
          </div>
        )}
      </section>

    </div>
  </div>
  )
}

export default App;