import React from "react";
import { FaRobot, FaStethoscope } from "react-icons/fa";

const HeroSection = () => {
  return (
    <section className="flex items-center justify-between px-8 py-12 bg-gray-100">
      {/* Robot Icon */}
      <div className="flex items-center justify-center w-1/3 text-blue-600">
        <FaRobot size={96} aria-label="Robot Icon" />
      </div>
      {/* Text with Stethoscope Icon */}
      <div className="w-2/3 pl-8">
        <p className="text-gray-700 text-lg flex items-start">
          <span className="mr-2 mt-1">
            <FaStethoscope 
              size={24} 
              color="#2563eb"
              aria-label="Stethoscope Icon" 
            />
          </span>
          Welcome to HealthBot! This tool is designed to assist you with your
          health-related concerns using cutting-edge technology. Let us help you
          stay informed and make better decisions for your well-being! You can either 
          type or dictate your queries. Get started with our chat interface below!
        </p>
      </div>
    </section>
  );
};

export default HeroSection;