// import React from 'react';

// function SentimentApp({ onLogout }) {
//   return (
//     <div className="p-6">
//       <header className="flex justify-between items-center mb-8">
//         <h1 className="text-3xl font-bold text-blue-500">Sentiment Scout</h1>
//         <button
//           onClick={onLogout}
//           className="px-4 py-2 bg-red-500 text-white rounded-md hover:bg-red-600 transition duration-200"
//         >
//           Logout
//         </button>
//       </header>
//       {/* Rest of your Sentiment Scout app content goes here */}
//     </div>
//   );
// }

// export default SentimentApp;



import React, { useState } from 'react';
import axios from 'axios';
import { Pie } from 'react-chartjs-2';
import { Chart as ChartJS, ArcElement, Tooltip, Legend } from 'chart.js';
// import './index.css';

ChartJS.register(ArcElement, Tooltip, Legend);

function SentimentApp() {
  const [url, setUrl] = useState('');
  const [sentimentData, setSentimentData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  // Handle sentiment analysis request
  const analyzeSentiment = async () => {
    setLoading(true);
    setError('');
    setSentimentData(null);

    try {
      const response = await axios.post(
        'https://your-backend-url.com/api/analyze', // Replace with your backend URL
        { url }
      );
      setSentimentData(response.data);
    } catch (err) {
      setError('Failed to fetch sentiment analysis. Please check the URL and try again.');
    } finally {
      setLoading(false);
    }
  };

  // Helper function for conditional color based on sentiment value
  const getSentimentColor = (score) => {
    if (score >= 0.7) return 'text-green-600'; // High positive
    if (score >= 0.4) return 'text-gray-600';  // Neutral
    return 'text-red-600';                    // High negative
  };

  // Determine overall sentiment badge text and color
  const getOverallSentiment = () => {
    if (!sentimentData) return '';
    const { positive, neutral, negative } = sentimentData;
    if (positive > negative && positive > neutral) return { label: 'Positive', color: 'bg-green-100 text-green-700' };
    if (negative > positive && negative > neutral) return { label: 'Negative', color: 'bg-red-100 text-red-700' };
    return { label: 'Neutral', color: 'bg-gray-100 text-gray-700' };
  };

  // Data for Pie Chart
  const chartData = {
    labels: ['Positive', 'Neutral', 'Negative'],
    datasets: [
      {
        label: 'Sentiment Distribution',
        data: [sentimentData?.positive, sentimentData?.neutral, sentimentData?.negative],
        backgroundColor: ['#34D399', '#A1A1AA', '#F87171'],
        hoverOffset: 8,
      },
    ],
  };

  const chartOptions = {
    plugins: {
      tooltip: {
        callbacks: {
          label: (context) => {
            const label = context.label || '';
            const value = context.raw !== undefined ? context.raw.toFixed(2) : '0.00';
            return `${label}: ${value}`;
          },
        },
      },
      legend: {
        position: 'bottom',
      },
    },
  };

  return (
    <div className="min-h-screen bg-gray-100 flex flex-col items-center justify-center p-6">
      <header className="text-center mb-8 animate-fadeIn">
        <h1 className="text-4xl font-bold text-blue-500">Sentiment Scout</h1>
        <p className="text-gray-600 mt-2">Analyze product sentiment from Amazon and Flipkart</p>
      </header>

      <div className="bg-white p-6 rounded-lg shadow-md w-full max-w-lg animate-fadeIn">
        <input
          type="text"
          className="w-full p-3 border border-gray-300 rounded mb-4 focus:outline-none focus:ring-2 focus:ring-blue-400 transition duration-200 ease-in-out transform hover:scale-105"
          placeholder="Enter Amazon or Flipkart product URL"
          value={url}
          onChange={(e) => setUrl(e.target.value)}
        />
        <button
          onClick={analyzeSentiment}
          className={`w-full bg-blue-500 hover:bg-blue-600 text-white p-3 rounded font-semibold flex items-center justify-center transition transform duration-200 ease-in-out ${loading ? 'opacity-70 cursor-not-allowed' : 'hover:scale-105'}`}
          disabled={loading}
        >
          {loading ? (
            <div className="w-5 h-5 border-4 border-t-transparent border-white rounded-full animate-spinner"></div>
          ) : (
            'Analyze Sentiment'
          )}
        </button>

        {error && (
          <div className="text-red-500 mt-4 animate-fadeIn">
            <p>{error}</p>
            <button
              onClick={analyzeSentiment}
              className="mt-2 px-4 py-2 bg-red-500 text-white rounded hover:bg-red-600 transition duration-200"
            >
              Retry
            </button>
          </div>
        )}

        {sentimentData && (
          <div className="mt-6 animate-fadeIn">
            <h2 className="text-2xl font-semibold text-gray-700">Sentiment Analysis Result</h2>

            {/* Overall Sentiment Badge with Pulse Animation */}
            <div className={`mt-4 px-3 py-1 rounded-full inline-block text-center font-semibold ${getOverallSentiment().color} animate-pulse`}>
              {getOverallSentiment().label}
            </div>

            <div className="mt-4 p-4 bg-gray-100 rounded animate-fadeIn">
              <p className="text-lg font-medium text-gray-800">Summary:</p>
              <p className="text-gray-700">{sentimentData.summary}</p>

              <div className="mt-4">
                <p className="font-semibold">Sentiment Scores:</p>
                <ul className="mt-2 space-y-1">
                  <li className="relative flex items-center">
                    <span className={`${getSentimentColor(sentimentData.positive)} mr-2`}>Positive:</span>
                    <span className="ml-2">{sentimentData.positive}</span>
                  </li>
                  <li className="relative flex items-center">
                    <span className={`${getSentimentColor(sentimentData.neutral)} mr-2`}>Neutral:</span>
                    <span className="ml-2">{sentimentData.neutral}</span>
                  </li>
                  <li className="relative flex items-center">
                    <span className={`${getSentimentColor(sentimentData.negative)} mr-2`}>Negative:</span>
                    <span className="ml-2">{sentimentData.negative}</span>
                  </li>
                </ul>
              </div>
            </div>

            {/* Pie Chart for Sentiment Distribution */}
            <div className="mt-6">
              <Pie data={chartData} options={chartOptions} />
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default SentimentApp;
