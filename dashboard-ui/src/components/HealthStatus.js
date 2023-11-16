import React, { useEffect, useState } from "react";
import "../App.css";

export default function HeathStatus() {
  const [isLoaded, setIsLoaded] = useState(false);
  const [stats, setStats] = useState({});
  const [error, setError] = useState(null);

  const getStats = () => {
    fetch(
      `http://kafkaprod1.westus3.cloudapp.azure.com:8120/usage/health_status`
    )
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
        <h1>Latest Health Check Stats</h1>
        <table className={"StatsTable"}>
          <tbody>
            <tr>
              <th>Health Check Status</th>
            </tr>
            <tr>
              <td># Reciever Status: {stats["receiver"]}</td>
            </tr>
            <tr>
              <td># Processing Status: {stats["processing"]}</td>
            </tr>
            <tr>
              <td colspan="2">Storage Status: {stats["storage"]}</td>
            </tr>
            <tr>
              <td colspan="2">Audit Status: {stats["audit"]}</td>
            </tr>
          </tbody>
        </table>
        <h3>Last Updated: {stats["last_updated"]}</h3>
      </div>
    );
  }
}
