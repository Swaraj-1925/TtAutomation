import {useLocation} from "react-router-dom";
import axios from "axios";
import {useEffect, useState} from "react";
import Background from "../assets/83f8c7639382e6aaa7e15ee7958f31ea.jpg";
import sadBackground from "../assets/sad.jpg";

const Home = () => {
    const location = useLocation();
    const [data, setData] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [deleteLoading, setDeleteLoading] = useState(false);
    const [deleteMessage, setDeleteMessage] = useState(null);

    useEffect(() => {
        const fetchData = async () => {
            setLoading(true);
            setError(null);

            const queryParams = new URLSearchParams(location.search);
            const userId = queryParams.get("user_id");

            if (userId) {
                try {
                    const response = await axios.get(`http://localhost:8000/home?user_id=${userId}`);
                    setData(response.data);
                } catch (err) {
                    setError(err.message);
                } finally {
                    setLoading(false);
                }
            } else {
                setError("User ID not provided");
                setLoading(false);
            }
        };

        fetchData();
    }, [location.search]);

    const handleDelete = async () => {
        setDeleteLoading(true);
        setDeleteMessage(null);

        const queryParams = new URLSearchParams(location.search);
        const userId = queryParams.get("user_id");

        if (!userId) {
            setDeleteMessage("User ID not provided");
            setDeleteLoading(false);
            return;
        }

        try {
            await axios.get(`http://localhost:8000/delete?user_id=${userId}`);
            setData(null); // This will trigger the UI change
            setDeleteMessage("Automation data deleted successfully!");
        } catch (err) {
            setDeleteMessage("Failed to delete automation data: " + err.message);
        } finally {
            setDeleteLoading(false);
        }
    };

    if (loading) return <div>Loading...</div>;
    if (error) return <div>Error: {error}</div>;

    return (
        <div>
            <div className="bg-white-300 relative overflow-hidden h-screen">
                {/* Conditional Image Based on `data` */}
                <img
                    src={data ? Background : sadBackground} // Change to new image if data is deleted
                    className="absolute h-full w-full object-contain scale-125"
                    alt="Background"
                />
                <div className="inset-0 bg-black opacity-25 absolute"></div>
                <div className="container mx-auto px-6 md:px-12 relative z-10 flex items-center py-32 xl:py-40">
                    <div className="w-full font-mono flex flex-col items-center relative z-10">
                        {/* Conditional Text Based on `data` */}
                        {data ? (
                            <>
                                <h1 className="font-extrabold text-5xl text-center text-white leading-tight mt-4">
                                    Say Goodbye to Excel Nightmares!
                                </h1>
                                <p className="font-extrabold text-3xl text-center text-white my-44 animate-bounce">
                                    Checking timetables used to be a chaotic mess—like wrestling a
                                    spreadsheet octopus. We’ve tamed it for you. Relax, you’ve earned
                                    it!
                                </p>
                                <button
                                    onClick={handleDelete}
                                    className="px-6 py-3 bg-red-600 text-white font-bold rounded-lg hover:bg-red-700 transition duration-300"
                                    disabled={deleteLoading}
                                >
                                    {deleteLoading ? "Deleting..." : "Get Rid of Automation"}
                                </button>
                            </>
                        ) : (
                            <>
                                <h1 className="font-extrabold text-5xl text-center text-white leading-tight mt-4">
                                    Automation Removed!
                                </h1>
                                <p className="font-extrabold text-3xl text-center text-white my-44">
                                    Your schedules have been successfully deleted.
                                </p>
                            </>
                        )}

                        {/* Deletion Message */}
                        {deleteMessage && <p className="text-white mt-4">{deleteMessage}</p>}
                    </div>
                </div>
            </div>
        </div>

    );
};
export default Home;