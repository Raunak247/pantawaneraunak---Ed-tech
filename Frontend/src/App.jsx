import { useEffect, useState } from 'react';
import { Header } from './Component/Header';
import { Footer } from './Component/Footer';
import { HomePage } from './Pages/HomePage';
import { ResultsPage } from './Pages/ResultPage';
import { SubjectsPage } from './Pages/SubjectsPage';
import { AuthPage } from './Pages/Login';
const App = () => {
  const [user, setUser] = useState(null);
  const [currentPage, setCurrentPage] = useState('home');
  const [selectedSubject, setSelectedSubject] = useState(null);
  const [assessmentId, setAssessmentId] = useState(null);



  useEffect(() => {
    try {
      const storedUser = localStorage.getItem('user');
      if (storedUser) {
        setUser(JSON.parse(storedUser));
      }
    } catch (error) {
      console.error("Failed to parse stored user:", error);
      setUser(null); // optional: clear state if parsing fails
    }
  }, []);

  const handleLogin = (userData) => {
    setUser(userData);
    localStorage.setItem('user', JSON.stringify(userData));
    setCurrentPage('home');
  };

  const handleLogout = () => {
    setUser(null);
    localStorage.removeItem('user');
    setCurrentPage('home');
  };

  // Render appropriate page
  const renderPage = () => {
    if (!user && currentPage !== 'home') {
      return <AuthPage onLogin={handleLogin} />;
    }

    switch (currentPage) {
      case 'home':
        return <HomePage user={user} setCurrentPage={setCurrentPage} />;
      case 'subjects':
        return (
          <SubjectsPage
            user={user}
            setCurrentPage={setCurrentPage}
            setSelectedSubject={setSelectedSubject}
          />
        );
      case 'assessment':
        return (
          <AssessmentPage
            user={user}
            selectedSubject={selectedSubject}
            setCurrentPage={setCurrentPage}
            setAssessmentId={setAssessmentId}
          />
        );
      case 'results':
        return (
          <ResultsPage
            user={user}
            selectedSubject={selectedSubject}
            assessmentId={assessmentId}
            setCurrentPage={setCurrentPage}
          />
        );
      case 'dashboard':
        return <DashboardPage user={user} />;
      case 'profile':
        return <ProfilePage user={user} />;
      default:
        return <HomePage user={user} setCurrentPage={setCurrentPage} />;
    }
  };

  return (
    <div className="min-h-screen flex flex-col bg-gray-50">
      {user ? (
        <>
          <Header
            user={user}
            onLogout={handleLogout}
            currentPage={currentPage}
            setCurrentPage={setCurrentPage}
          />
          <main className="flex-1">
            {renderPage()}
          </main>
          <Footer />
        </>
      ) : (
        currentPage === 'home' ? (
          <>
            <Header
              user={null}
              onLogout={handleLogout}
              currentPage={currentPage}
              setCurrentPage={setCurrentPage}
            />
            <main className="flex-1">
              <HomePage user={null} setCurrentPage={setCurrentPage} />
              <div className="container mx-auto px-4 pb-12">
                <div className="max-w-md mx-auto">
                  <AuthPage onLogin={handleLogin} />
                </div>
              </div>
            </main>
            <Footer />
          </>
        ) : (
          <AuthPage onLogin={handleLogin} />
        )
      )}
    </div>
  );
};

export default App;