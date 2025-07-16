import React, { useEffect, useState } from 'react';
import axios from '../api';
import MetricsChart from '../components/MetricsChart';

function Dashboard() {
  const [metrics, setMetrics] = useState([]);

  useEffect(() => {
    const fetchMetrics = async () => {
      try {
        const response = await axios.get('/metrics');
        setMetrics(response.data);
      } catch (error) {
        console.error('Failed to fetch metrics:', error);
      }
    };

    fetchMetrics();
    const interval = setInterval(fetchMetrics, 5000); // every 5s
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="dashboard">
      <MetricsChart data={metrics} />
    </div>
  );
}

export default Dashboard;
