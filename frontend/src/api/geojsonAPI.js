export const fetchGeoJSON = async (type) => {
  const token = localStorage.getItem('token'); // Récupère le token depuis le stockage local
  try {
    const response = await fetch(`${process.env.REACT_APP_IP_SERV}/api/${type}`, {
      method: 'GET',
      headers: {
        'Authorization': token,
      },
    });

    if (!response.ok) {
      throw new Error('Network response was not ok');
    }

    const data = await response.json();
    console.log(`${type} data fetched:`, data);  // Affichez les données dans la console
    return data;
  } catch (error) {
    console.error(`Error fetching ${type} data:`, error);
  }
};