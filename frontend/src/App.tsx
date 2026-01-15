import { useState, useEffect } from 'react';
import './App.css';
import MapSelector from "./Components/MapSelector.tsx";
import type { LatLng } from './Components/MapSelector.tsx';
import { CreatableMultiSelect, type Option } from './Components/CreatableMultiSelect.tsx';
import { defaultJyotishSchools, defaultRemedyCategories } from './config.tsx';
import axios from 'axios';
import ReportEditor from './Components/ReportEditor.tsx';
import { useLocalStorage } from './Hooks/useLocalStorage.tsx';
import toast, { Toaster } from 'react-hot-toast';

function App() {
  const [day, setDay] = useLocalStorage<string>("day", "");
  const [month, setMonth] = useLocalStorage<string>("month", "");
  const [year, setYear] = useLocalStorage<string>("year", "");
  const [hours, setHours] = useLocalStorage<string>("hours", "");
  const [minutes, setMinutes] = useLocalStorage<string>("minutes", "");

  const [latitude, setLatitude] = useLocalStorage<number>("latitude", 28.6139);
  const [longitude, setLongitude] = useLocalStorage<number>("longitude", 77.2090);

  const [incRemedyCategories, setIncRemedyCategories] = useLocalStorage<readonly Option[]>("incRemedyCategories", []);

  const [excRemedyCategories, setExcRemedyCategories] = useLocalStorage<readonly Option[]>("excRemedyCategories", []);

  const [jyotishSchools, setJyotishSchools] = useLocalStorage<readonly Option[]>("jyotishSchools", []);

  const [language, setLanguage] = useLocalStorage<string>("language", "");

  const [loading, setLoading] = useState<boolean>(false);
  const [showClear, setShowClear] = useState(false);

  const [kundliImageSrc, setKundliImageSrc] = useState<string | null>("1");
  const [dashaContent, setDashaContent] = useState<string>("");
  const [gocharImageSrc, setGocharImageSrc] = useState<string | null>("1");
  const [reportContent, setReportContent] = useState<string>("");

  const isFormInvalid = !year || !month || !day || !hours || !minutes || !latitude || !longitude || loading;
  const hasOverlap = incRemedyCategories.some(a =>
    excRemedyCategories.some(b => a.value === b.value)
  );

  useEffect(() => {
    const jobStatus = localStorage.getItem("report_generation");

    if (jobStatus === "running") {
      toast("Resuming report generation…", {
        icon: "🔄",
      });

      // Prevent double-trigger
      setLoading(true);

      // Resume generation using stored state
      handleGenerateReport();
    }
  }, []);

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

  const handleClearAll = () => {
    // Form fields
    setDay("");
    setMonth("");
    setYear("");
    setHours("");
    setMinutes("");

    setLatitude(28.6139);
    setLongitude(77.2090);

    setIncRemedyCategories([]);
    setExcRemedyCategories([]);
    setJyotishSchools([]);
    setLanguage("");

    // Generated content
    setKundliImageSrc(null);
    setGocharImageSrc(null);
    setReportContent("");
    setDashaContent("");

    setShowClear(false);
    ["day", "month", "year", "hours", "minutes", "latitude", "longitude", "incRemedyCategories", "excRemedyCategories", "jyotishSchools", "language",].forEach(key => localStorage.removeItem(key));

    toast.success("Form cleared. Ready for a new report.", {
      icon: "🌱",
    });
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
    if (loading) {
      toast("Previous session detected. Continuing analysis.", {
        icon: "🧘",
      });
      return;
    }

    if (isFormInvalid) {
      toast("Please fill all date & time fields", {
        icon: "🕰️",
      });
      return;
    }
    if (hasOverlap) {
      toast("Inclusions and exclusions overlap", {
        icon: "⚖️",
      });
      return;
    }

    const birth_details = {
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
      toast("Generating your report…", {
        icon: "✨",
      });
      const kundliResponse = await axios.post('/api/generate-kundli', birth_details, { responseType: 'blob' });
      setKundliImageSrc(URL.createObjectURL(kundliResponse.data));

      const gocharResponse = await axios.post('/api/generate-gochar', birth_details, { responseType: 'blob' });
      setGocharImageSrc(URL.createObjectURL(gocharResponse.data));

      localStorage.setItem("report_generation", "Started");

      const analysisResponse = await axios.post('/api/generate-prompt', analysis_payload);
      console.log("Report Generated:", analysisResponse.data);

      localStorage.setItem("report_generation", "Finished");

      setReportContent(analysisResponse.data.analysis_result);
      setDashaContent(analysisResponse.data.dasha);
      setLoading(false);
      toast.success("Report generated successfully");
    } catch (error) {
      localStorage.setItem("report_generation", "Finished");
      setLoading(false);
      console.error("Error generating report:", error);
      toast.error("Failed to generate report");
    }
  };

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      const target = e.target as HTMLElement;

      // Ignore when typing in inputs, textareas, or selects
      const isTyping =
        target.tagName === "INPUT" ||
        target.tagName === "TEXTAREA" ||
        target.getAttribute("role") === "textbox";

      if (isTyping) return;

      // Enter → Generate
      if (e.key === "Enter") {
        e.preventDefault();

        if (!isFormInvalid && !hasOverlap && !loading) {
          handleGenerateReport();
        }
      }

      // Escape → Clear
      if (e.key === "Escape") {
        e.preventDefault();
        handleClearAll();
      }
    };

    window.addEventListener("keydown", handleKeyDown);

    return () => {
      window.removeEventListener("keydown", handleKeyDown);
    };
  }, [
    handleGenerateReport,
    handleClearAll,
    isFormInvalid,
    hasOverlap,
    loading,
  ]);


  return (
    <div className="relative min-h-screen overflow-hidden bg-gradient-to-br from-slate-50 via-white to-indigo-100/40">
      <Toaster />
      <div className="relative z-10 max-w-7xl mx-auto px-6 py-12 space-y-12">

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
        <div className="relative bg-white/80 backdrop-blur border border-slate-200/70 shadow-[0_8px_30px_-12px_rgba(0,0,0,0.08)] p-8 space-y-10">
          <img
            src="/peacock2.gif"
            alt="Peacock"
            className="
              hidden md:block
              absolute
              -top-42 -right-13
              w-70 h-auto
              pointer-events-none
              select-none
            "
          />
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
                    type="text"
                    inputMode='numeric'
                    pattern='[0-9]*'
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
              <label className="text-xs tracking-wide uppercase text-slate-400 pl-[2px]">Include Remedies (उपाय)</label>
              <CreatableMultiSelect
                value={incRemedyCategories}
                onChange={setIncRemedyCategories}
                placeholder="Select categories"
                defaultOptions={defaultRemedyCategories}
              />
            </div>

            <div>
              <label className="text-xs tracking-wide uppercase text-slate-400 pl-[2px]">Exclude Remedies (उपाय)</label>
              <CreatableMultiSelect
                value={excRemedyCategories}
                onChange={setExcRemedyCategories}
                placeholder="Select categories"
                defaultOptions={defaultRemedyCategories}
              />
            </div>

            <div>
              <label className="text-xs tracking-wide uppercase text-slate-400 pl-[2px]">Jyotish Schools (ज्योतिष परंपराएँ)</label>
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

          <div className="pt-6 border-t border-slate-200 flex items-center gap-12">
            <button onClick={handleGenerateReport} disabled={(isFormInvalid || hasOverlap)} className="bg-amber-400 hover:bg-amber-500 text-slate-700 shadow-sm hover:shadow-md disabled:bg-slate-300 px-8 py-3 rounded-xl font-medium transition-all">
              {loading ? "Generating..." : "Generate Report"}
            </button>

            {!showClear ? (
              <button
                onClick={() => setShowClear(true)}
                className="px-6 py-3 rounded-xl border border-slate-300 text-slate-600 hover:bg-slate-50 hover:border-slate-400 transition font-medium"
              >
                Reset form
              </button>
            ) : (
              <button
                onClick={handleClearAll}
                className="px-6 py-2.5 rounded-lg bg-indigo-50 hover:bg-indigo-100 text-indigo-700 border border-indigo-200 shadow-sm transition font-medium"
              >
                Confirm clear
              </button>
            )}
          </div>

        </div>

        {/* Report */}
        <section className="space-y-6">
          <h2 className="text-lg font-medium text-slate-900 border-l-2 border-indigo-300/60 pl-3">Report</h2>
          {kundliImageSrc && gocharImageSrc && (
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