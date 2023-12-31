import React, { useEffect, useState } from "react";
import "../App.css";

export default function AppStats() {
  const [isLoaded, setIsLoaded] = useState(false);
  const [stats, setStats] = useState({});
  const [error, setError] = useState(null);

  const getStats = () => {
    fetch(`http://kafkaprod1.westus3.cloudapp.azure.com/processing/usage/stats`)
      .then((res) => res.json())
      .then(
        (result) => {
          console.log("Received Stats");
          setStats(result);
          setIsLoaded(true);
        },
        (error) => {
          setError(error);
          setIsLoaded(true);
        }
      );
  };
  useEffect(() => {
    const interval = setInterval(() => getStats(), 2000); // Update every 2 seconds
    return () => clearInterval(interval);
  }, [getStats]);

  if (error) {
    return <div className={"error"}>Error found when fetching from API</div>;
  } else if (isLoaded === false) {
    return <div>Loading...</div>;
  } else if (isLoaded === true) {
    return (
      <div>
        <h1>Latest Stats</h1>
        <table className={"StatsTable"}>
          <tbody>
            <tr>
              <th>Power Usage</th>
              <th>Temperature Readings</th>
            </tr>
            <tr>
              <td>
                # Power Usage Readings: {stats["num_powerusage_readings"]}
              </td>
              <td>
                # Temperature Readings: {stats["num_temperature_readings"]}
              </td>
            </tr>
            <tr>
              <td colspan="2">
                Max Watts Readings: {stats["max_watts_reading"]}
              </td>
            </tr>
            <tr>
              <td colspan="2">
                Max Temperature Reading: {stats["max_temperature_reading"]}
              </td>
            </tr>
          </tbody>
        </table>
        <h3>Last Updated: {stats["last_updated"]}</h3>
      </div>
    );
  }
}
