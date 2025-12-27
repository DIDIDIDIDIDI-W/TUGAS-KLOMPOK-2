
import React, { useState, useEffect, useMemo, useCallback } from 'react';
import * as XLSX from 'xlsx';
import { ScatterChart, Scatter, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, Line } from 'recharts';
import { DataRow, RegressionResult } from './types.ts';
import { UploadIcon, ChartIcon, ResetIcon } from './components/icons.tsx';

const StatCard = ({ title, value, description }: { title: string; value: string; description: string }) => (
    <div className="bg-slate-800/50 p-4 rounded-lg shadow-md border border-slate-700">
        <h3 className="text-sm font-medium text-slate-400">{title}</h3>
        <p className="text-2xl font-bold text-cyan-400 mt-1">{value}</p>
        <p className="text-xs text-slate-500 mt-1">{description}</p>
    </div>
);

const FileUpload = ({ onFileUpload, setLoading, setError }: { onFileUpload: (file: File) => void; setLoading: (loading: boolean) => void; setError: (error: string) => void; }) => {
    const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
        const file = event.target.files?.[0];
        if (file) {
            if (file.type === 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' || file.name.endsWith('.csv')) {
                setError('');
                setLoading(true);
                onFileUpload(file);
            } else {
                setError('Please upload a valid Excel (.xlsx) or CSV (.csv) file.');
            }
        }
    };

    const handleDragOver = (event: React.DragEvent<HTMLLabelElement>) => {
        event.preventDefault();
    };

    const handleDrop = (event: React.DragEvent<HTMLLabelElement>) => {
        event.preventDefault();
        const file = event.dataTransfer.files?.[0];
        if (file) {
            if (file.type === 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' || file.name.endsWith('.csv')) {
                setError('');
                setLoading(true);
                onFileUpload(file);
            } else {
                setError('Please upload a valid Excel (.xlsx) or CSV (.csv) file.');
            }
        }
    };

    return (
        <div className="w-full max-w-2xl mx-auto text-center">
            <label
                htmlFor="file-upload"
                className="relative block w-full p-8 border-2 border-dashed rounded-lg cursor-pointer border-slate-600 hover:border-cyan-400 transition-colors"
                onDragOver={handleDragOver}
                onDrop={handleDrop}
            >
                <UploadIcon className="w-16 h-16 mx-auto text-slate-500" />
                <span className="block mt-4 text-xl font-semibold text-slate-300">
                    Drag & Drop your file here
                </span>
                <span className="block mt-1 text-sm text-slate-400">
                    or <span className="font-semibold text-cyan-400">click to browse</span>
                </span>
                <span className="block mt-2 text-xs text-slate-500">
                    Supports .xlsx and .csv files
                </span>
                <input id="file-upload" name="file-upload" type="file" className="sr-only" onChange={handleFileChange} accept=".xlsx, .csv" />
            </label>
        </div>
    );
};

export default function App() {
    const [data, setData] = useState<DataRow[]>([]);
    const [headers, setHeaders] = useState<string[]>([]);
    const [fileName, setFileName] = useState<string>('');
    const [selectedX, setSelectedX] = useState<string>('');
    const [selectedY, setSelectedY] = useState<string>('');
    const [regressionResult, setRegressionResult] = useState<RegressionResult | null>(null);
    const [isLoading, setIsLoading] = useState<boolean>(false);
    const [error, setError] = useState<string>('');

    const handleFileUpload = (file: File) => {
        const reader = new FileReader();
        reader.onload = (e) => {
            try {
                const binaryStr = e.target?.result;
                const workbook = XLSX.read(binaryStr, { type: 'binary' });
                const sheetName = workbook.SheetNames[0];
                const worksheet = workbook.Sheets[sheetName];
                const jsonData: DataRow[] = XLSX.utils.sheet_to_json(worksheet, { defval: "" });

                if (jsonData.length > 0) {
                    setData(jsonData);
                    const firstRowHeaders = Object.keys(jsonData[0]);
                    setHeaders(firstRowHeaders);
                    const numericHeaders = firstRowHeaders.filter(h => jsonData.every(row => !isNaN(parseFloat(String(row[h])))));
                    if (numericHeaders.length >= 2) {
                        setSelectedX(numericHeaders[0]);
                        setSelectedY(numericHeaders[1]);
                    } else if (numericHeaders.length === 1) {
                        setSelectedX(numericHeaders[0]);
                        setSelectedY('');
                    } else {
                        setSelectedX('');
                        setSelectedY('');
                    }
                    setFileName(file.name);
                    setError('');
                } else {
                    setError('The uploaded file is empty or could not be read.');
                }
            } catch (err) {
                console.error(err);
                setError('Failed to parse the file. Please ensure it is a valid format.');
                setData([]);
                setHeaders([]);
            } finally {
                setIsLoading(false);
            }
        };
        reader.readAsBinaryString(file);
    };

    const handleReset = () => {
        setData([]);
        setHeaders([]);
        setFileName('');
        setSelectedX('');
        setSelectedY('');
        setRegressionResult(null);
        setError('');
        setIsLoading(false);
    };

    const numericHeaders = useMemo(() => {
        if (data.length === 0) return [];
        return headers.filter(h => data.every(row => typeof row[h] === 'number' || (typeof row[h] === 'string' && !isNaN(parseFloat(row[h])))));
    }, [data, headers]);

    useEffect(() => {
        if (data.length > 0 && selectedX && selectedY && selectedX !== selectedY) {
            const points = data
                .map(row => ({
                    x: parseFloat(String(row[selectedX])),
                    y: parseFloat(String(row[selectedY])),
                }))
                .filter(p => !isNaN(p.x) && !isNaN(p.y));

            if (points.length < 2) {
                setRegressionResult(null);
                return;
            }

            const n = points.length;
            let sumX = 0, sumY = 0, sumXY = 0, sumX2 = 0, sumY2 = 0;

            for (const p of points) {
                sumX += p.x;
                sumY += p.y;
                sumXY += p.x * p.y;
                sumX2 += p.x * p.x;
                sumY2 += p.y * p.y;
            }

            const numeratorSlope = n * sumXY - sumX * sumY;
            const denominatorSlope = n * sumX2 - sumX * sumX;
            
            if (denominatorSlope === 0) {
                setRegressionResult(null);
                return;
            }

            const slope = numeratorSlope / denominatorSlope;
            const intercept = (sumY - slope * sumX) / n;

            const rNumerator = (n * sumXY - sumX * sumY);
            const rDenominator = Math.sqrt((n * sumX2 - sumX * sumX) * (n * sumY2 - sumY * sumY));
            const r = rDenominator === 0 ? 0 : rNumerator / rDenominator;
            const rSquared = r * r;

            const xValues = points.map(p => p.x);
            const minX = Math.min(...xValues);
            const maxX = Math.max(...xValues);

            setRegressionResult({
                slope,
                intercept,
                rSquared,
                lineData: [
                    { x: minX, y: slope * minX + intercept },
                    { x: maxX, y: slope * maxX + intercept },
                ],
            });
        } else {
            setRegressionResult(null);
        }
    }, [data, selectedX, selectedY]);

    const chartData = useMemo(() => {
        if (!selectedX || !selectedY) return [];
        return data.map(row => ({
            x: parseFloat(String(row[selectedX])),
            y: parseFloat(String(row[selectedY])),
        })).filter(p => !isNaN(p.x) && !isNaN(p.y));
    }, [data, selectedX, selectedY]);

    const renderContent = () => {
        if (isLoading) {
            return <div className="text-center text-slate-300">Parsing your file...</div>;
        }
        if (error) {
            return <div className="text-center text-red-400 bg-red-900/50 p-4 rounded-lg">{error}</div>;
        }
        if (data.length === 0) {
            return <FileUpload onFileUpload={handleFileUpload} setLoading={setIsLoading} setError={setError} />;
        }

        return (
            <div className="w-full space-y-6">
                <header className="flex flex-col sm:flex-row justify-between items-center gap-4 p-4 bg-slate-800/50 border border-slate-700 rounded-lg">
                    <div className="flex items-center gap-3">
                        <ChartIcon className="w-6 h-6 text-cyan-400" />
                        <h2 className="text-lg font-semibold text-slate-200 truncate" title={fileName}>{fileName}</h2>
                    </div>
                    <button onClick={handleReset} className="flex items-center gap-2 px-4 py-2 text-sm font-medium text-white bg-red-600 rounded-md hover:bg-red-700 transition-colors focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-slate-900 focus:ring-red-500">
                        <ResetIcon className="w-4 h-4" />
                        Upload New File
                    </button>
                </header>

                <main className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                    <div className="lg:col-span-1 space-y-6">
                        <div className="p-4 bg-slate-800/50 border border-slate-700 rounded-lg">
                            <h3 className="font-semibold text-slate-200 mb-4">Analysis Variables</h3>
                            <div className="space-y-4">
                                <div>
                                    <label htmlFor="x-axis" className="block text-sm font-medium text-slate-400 mb-1">X-Axis (Independent)</label>
                                    <select id="x-axis" value={selectedX} onChange={e => setSelectedX(e.target.value)} className="w-full p-2 bg-slate-700 border border-slate-600 rounded-md focus:ring-cyan-500 focus:border-cyan-500 transition">
                                        <option value="">Select column</option>
                                        {numericHeaders.map(h => <option key={h} value={h}>{h}</option>)}
                                    </select>
                                </div>
                                <div>
                                    <label htmlFor="y-axis" className="block text-sm font-medium text-slate-400 mb-1">Y-Axis (Dependent)</label>
                                    <select id="y-axis" value={selectedY} onChange={e => setSelectedY(e.target.value)} className="w-full p-2 bg-slate-700 border border-slate-600 rounded-md focus:ring-cyan-500 focus:border-cyan-500 transition">
                                        <option value="">Select column</option>
                                        {numericHeaders.filter(h => h !== selectedX).map(h => <option key={h} value={h}>{h}</option>)}
                                    </select>
                                </div>
                            </div>
                        </div>
                        {regressionResult && (
                            <div className="p-4 bg-slate-800/50 border border-slate-700 rounded-lg space-y-4">
                                <h3 className="font-semibold text-slate-200 mb-2">Regression Statistics</h3>
                                <StatCard title="R-Squared" value={regressionResult.rSquared.toFixed(4)} description="Model fit quality" />
                                <StatCard title="Slope (m)" value={regressionResult.slope.toFixed(4)} description={`Change in Y per unit of X`} />
                                <StatCard title="Y-Intercept (b)" value={regressionResult.intercept.toFixed(4)} description="Value of Y when X is 0" />
                                <div className="pt-2">
                                    <h4 className="text-sm font-medium text-slate-400">Regression Equation</h4>
                                    <p className="text-lg font-mono text-emerald-400 bg-slate-900 p-2 rounded-md mt-1 text-center">
                                        y = {regressionResult.slope.toFixed(2)}x + {regressionResult.intercept.toFixed(2)}
                                    </p>
                                </div>
                            </div>
                        )}
                    </div>

                    <div className="lg:col-span-2 p-4 bg-slate-800/50 border border-slate-700 rounded-lg min-h-[500px]">
                        <h3 className="font-semibold text-slate-200 mb-4">Data Visualization</h3>
                        {selectedX && selectedY ? (
                            <ResponsiveContainer width="100%" height="100%">
                                <ScatterChart margin={{ top: 20, right: 20, bottom: 20, left: 20 }}>
                                    <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                                    <XAxis type="number" dataKey="x" name={selectedX} unit="" stroke="#9ca3af" domain={['dataMin', 'dataMax']} />
                                    <YAxis type="number" dataKey="y" name={selectedY} unit="" stroke="#9ca3af" domain={['dataMin', 'dataMax']} />
                                    <Tooltip cursor={{ strokeDasharray: '3 3' }} contentStyle={{ backgroundColor: '#1f2937', border: '1px solid #374151' }} />
                                    <Legend />
                                    <Scatter name="Data Points" data={chartData} fill="#22d3ee" shape="circle" />
                                    {regressionResult && regressionResult.lineData.length > 0 && (
                                        <Line
                                            dataKey="y"
                                            data={regressionResult.lineData}
                                            stroke="#10b981"
                                            dot={false}
                                            activeDot={false}
                                            strokeWidth={2}
                                            name="Regression Line"
                                            legendType="line"
                                        />
                                    )}
                                </ScatterChart>
                            </ResponsiveContainer>
                        ) : (
                            <div className="flex items-center justify-center h-full text-slate-500">
                                <p>Please select both X and Y axis columns to display the chart.</p>
                            </div>
                        )}
                    </div>
                </main>
            </div>
        );
    };

    return (
        <div className="min-h-screen flex flex-col items-center justify-center p-4 sm:p-6 lg:p-8">
            <div className="w-full max-w-7xl mx-auto">
                <div className="text-center mb-8">
                    <h1 className="text-4xl font-bold tracking-tight text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-blue-500">
                        Excel Regression Analyzer
                    </h1>
                    <p className="mt-3 max-w-2xl mx-auto text-lg text-slate-400">
                        Upload your data to instantly visualize relationships and perform linear regression.
                    </p>
                </div>
                {renderContent()}
            </div>
        </div>
    );
}
