import React from 'react';
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer
} from 'recharts';

function MetricsChart({ data }) {
  return (
    <div className="chart-container">
      <h2>Training Metrics</h2>
      <ResponsiveContainer width="100%" height={400}>
        <LineChart data={data}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="round" />
          <YAxis />
          <Tooltip />
          <Legend />
          <Line type="monotone" dataKey="loss" stroke="#8884d8" />
          <Line type="monotone" dataKey="accuracy" stroke="#82ca9d" />
          <Line type="monotone" dataKey="epsilon" stroke="#ff7300" />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}

export default MetricsChart;
