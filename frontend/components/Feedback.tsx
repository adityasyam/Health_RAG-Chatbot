import React from "react";

const FeedbackBox = () => {
  return (
    <footer className="bg-gray-100 py-6 px-8 border-t border-gray-300">
      <div className="text-center">
        <h2 className="text-gray-700 text-lg font-semibold">
          We value your feedback!
        </h2>
        <p className="text-gray-600 mb-4">
          Help us improve by sharing your thoughts.
        </p>
        <a
          href="https://forms.gle/mir66sGQKi1NF1nS8"
          target="_blank"
          rel="noopener noreferrer"
          className="text-blue-600 hover:underline text-sm"
        >
          Fill out our feedback form
        </a>
      </div>
    </footer>
  );
};

export default FeedbackBox;
