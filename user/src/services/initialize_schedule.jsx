import axios from "axios";
export const initializeSchedule = async (formData) => {
    try {
        // Construct query parameters
        const queryParams = new URLSearchParams({
            user_id: formData.user_id,
            department: formData.department,
            division: formData.division,
            year: formData.year
        });

        // Make GET request with query parameters
        const response = await axios.get(`http://localhost:8000/?${queryParams}`, {
            // Add headers if needed
            headers: {
                'Content-Type': 'application/json',
            }
        });
        console.log("Successfully initializing schedule...");
        return response.data;
    }catch (error) {
        console.error(error);
        return "There was an error while initialize schedule";
    }

}