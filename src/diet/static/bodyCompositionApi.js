async function fetchApiData(apiEndpoint) {
  const response = await fetch(apiEndpoint);
  if (!response.ok) {
    throw new Error(`API request failed: ${response.status}`);
  }
  return await response.json();
}

export async function fetchBodyCompositionData(apiEndpoint) {
  const response = await fetchApiData(apiEndpoint);

  return {
    daily: response.bodyCompositions || [],
    monthly: response.monthlyStatistics || [],
  };
}
