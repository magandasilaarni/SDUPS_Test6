import React, { useRef, useState, useEffect } from "react";
import { BrowserRouter as Router, Route, Routes, Link } from "react-router-dom";
import FileUpload from "./components/FileUpload";
import Dashboard from "./components/Dashboard";
import ChiefDashboard from "./components/ChiefDashboard";
import 'bootstrap/dist/css/bootstrap.min.css';
import moment from "moment";

// Attempt to import the logo
let logoSrc;
try {
    logoSrc = require("./assets/logo.png"); // Make sure the logo is inside 'src/assets/'
} catch (error) {
    console.error("Logo file not found:", error);
    logoSrc = null; // Use fallback
}

const App = () => {
    const dashboardRef = useRef(null);
    const [currentTime, setCurrentTime] = useState(moment().format("MMMM Do YYYY, h:mm:ss a"));

    // Update the time every second
    useEffect(() => {
        const interval = setInterval(() => {
            setCurrentTime(moment().format("MMMM Do YYYY, h:mm:ss a"));
        }, 1000);
        return () => clearInterval(interval);
    }, []);

    const handleUploadSuccess = () => {
        if (dashboardRef.current) {
            dashboardRef.current.fetchFiles();
        }
    };

    return (
        <Router>
            {/* Navigation Bar */}
            <nav style={styles.navbar}>
                <div style={styles.navContent}>
                    {logoSrc ? (
                        <img src={logoSrc} alt="Logo" style={styles.logo} />
                    ) : (
                        <div style={styles.logoPlaceholder}>No Logo</div>
                    )}
                    <h2>School Governance and Operations Division</h2>
                </div>
                <div style={styles.navLinks}>
                    <Link style={styles.link} to="/">Upload File</Link>
                    <Link style={styles.link} to="/dashboard">Dashboard</Link>
                    <Link style={styles.link} to="/chief-dashboard">Chief Dashboard</Link>
                </div>
                <div style={styles.dateTime}>{currentTime}</div>
            </nav>

            {/* Main Content */}
            <div style={styles.container}>
                <Routes>
                    <Route path="/" element={<FileUpload onUploadSuccess={handleUploadSuccess} />} />
                    <Route path="/dashboard" element={<Dashboard ref={dashboardRef} />} />
                    <Route path="/chief-dashboard" element={<ChiefDashboard />} />
                    <Route path="*" element={<NotFound />} />
                </Routes>
            </div>

            {/* Footer */}
            <footer style={styles.footer}>
                <p>&copy; {new Date().getFullYear()} School Governance and Operations Division. All rights reserved.</p>
            </footer>
        </Router>
    );
};

// 404 Page
const NotFound = () => (
    <div style={styles.notFound}>
        <h1>404 - Page Not Found</h1>
        <Link to="/" style={styles.button}>Go Back Home</Link>
    </div>
);

// CSS-in-JS Styling
const styles = {
    navbar: {
        display: "flex",
        justifyContent: "space-between",
        alignItems: "center",
        padding: "15px 30px",
        background: "#212529",
        color: "#fff",
        boxShadow: "0px 4px 6px rgba(0, 0, 0, 0.1)",
    },
    navContent: { display: "flex", alignItems: "center", gap: "15px" },
    logo: { height: "50px" },
    logoPlaceholder: { width: "50px", height: "50px", background: "#ccc", display: "flex", alignItems: "center", justifyContent: "center" },
    navLinks: { display: "flex", gap: "20px" },
    link: { color: "#fff", textDecoration: "none", fontSize: "16px", fontWeight: "bold", padding: "8px 12px", transition: "0.3s" },
    dateTime: { fontSize: "14px", color: "#ddd" },
    container: { padding: "30px", minHeight: "70vh" },
    footer: {
        textAlign: "center",
        padding: "15px",
        background: "#212529",
        color: "#fff",
        marginTop: "20px",
    },
    notFound: { textAlign: "center", marginTop: "50px" },
    button: { padding: "10px 20px", background: "#007bff", color: "#fff", textDecoration: "none", borderRadius: "5px" },
};

export default App;
