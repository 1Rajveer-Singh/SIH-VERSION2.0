import React, { useState } from 'react'
import Navbar from '../components/Navbar'

interface FAQItem {
  question: string
  answer: string
  category: string
}

function HelpPage() {
  const [activeCategory, setActiveCategory] = useState('general')
  const [searchTerm, setSearchTerm] = useState('')
  const [expandedFAQ, setExpandedFAQ] = useState<number | null>(null)

  const faqData: FAQItem[] = [
    {
      question: "How do I interpret rockfall risk predictions?",
      answer: "Risk predictions are categorized as Low (0-0.3), Medium (0.3-0.7), and High (0.7-1.0). High-risk predictions require immediate attention and safety measures. The confidence score indicates how certain the AI model is about the prediction.",
      category: "predictions"
    },
    {
      question: "What should I do when I receive a high-risk alert?",
      answer: "Immediately evacuate personnel from the affected area, verify the alert through visual inspection if safe to do so, and contact the site safety supervisor. Follow your site's emergency protocols and document the incident.",
      category: "alerts"
    },
    {
      question: "How often are predictions updated?",
      answer: "Predictions are updated in real-time as new sensor data becomes available. The system continuously analyzes data from vibration sensors, temperature monitors, and drone imagery to provide the most current risk assessment.",
      category: "predictions"
    },
    {
      question: "How do I add a new monitoring device?",
      answer: "Navigate to the Devices page, click 'Add Device', fill in the device details including type, location, and calibration settings. Ensure the device is properly connected to the network before activation.",
      category: "devices"
    },
    {
      question: "Why is my device showing as offline?",
      answer: "Check the device's power supply, network connectivity, and physical condition. If the device appears damaged or continues to show offline status, contact technical support for assistance.",
      category: "devices"
    },
    {
      question: "How do I export prediction reports?",
      answer: "Go to the Reports page, select the prediction you want to export, and choose your preferred format (PDF, CSV, Excel, or JSON). The system will generate a comprehensive report including all analysis data.",
      category: "reports"
    },
    {
      question: "What data is included in the reports?",
      answer: "Reports include drone analysis results, sensor data trends, step-by-step AI processing stages, risk factor analysis, confidence scores, and actionable recommendations for site safety.",
      category: "reports"
    },
    {
      question: "How do I change my password?",
      answer: "Go to Settings > Profile, scroll down to the Security section, and click 'Change Password'. You'll need to enter your current password and confirm the new one.",
      category: "general"
    },
    {
      question: "Who can I contact for technical support?",
      answer: "For technical support, use the contact form below or email support@rockfallsystem.com. Include your username, site ID, and detailed description of the issue.",
      category: "general"
    }
  ]

  const categories = [
    { id: 'general', name: 'General', icon: '❓' },
    { id: 'predictions', name: 'Predictions', icon: '🤖' },
    { id: 'alerts', name: 'Alerts', icon: '🚨' },
    { id: 'devices', name: 'Devices', icon: '📱' },
    { id: 'reports', name: 'Reports', icon: '📊' }
  ]

  const filteredFAQs = faqData.filter(faq => 
    (activeCategory === 'general' || faq.category === activeCategory) &&
    (searchTerm === '' || 
     faq.question.toLowerCase().includes(searchTerm.toLowerCase()) ||
     faq.answer.toLowerCase().includes(searchTerm.toLowerCase()))
  )

  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />
      
      <div className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <div className="px-4 py-6 sm:px-0">
          <div className="mb-8">
            <h1 className="text-3xl font-bold text-gray-900">Help Center</h1>
            <p className="mt-2 text-gray-600">
              Find answers to common questions and get help with the Rockfall Prediction System
            </p>
          </div>

          {/* Search Bar */}
          <div className="mb-6">
            <div className="relative">
              <input
                type="text"
                placeholder="Search for help..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              />
              <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                <svg className="h-5 w-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                </svg>
              </div>
            </div>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
            {/* Categories Sidebar */}
            <div className="lg:col-span-1">
              <div className="bg-white rounded-lg shadow p-6">
                <h2 className="text-lg font-semibold text-gray-900 mb-4">Categories</h2>
                <nav className="space-y-2">
                  {categories.map((category) => (
                    <button
                      key={category.id}
                      onClick={() => setActiveCategory(category.id)}
                      className={`w-full text-left px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                        activeCategory === category.id
                          ? 'bg-blue-100 text-blue-700'
                          : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100'
                      }`}
                    >
                      {category.icon} {category.name}
                    </button>
                  ))}
                </nav>
              </div>

              {/* Quick Links */}
              <div className="bg-white rounded-lg shadow p-6 mt-6">
                <h2 className="text-lg font-semibold text-gray-900 mb-4">Quick Links</h2>
                <div className="space-y-3">
                  <a href="#contact" className="block text-blue-600 hover:text-blue-800 text-sm">
                    📧 Contact Support
                  </a>
                  <a href="#videos" className="block text-blue-600 hover:text-blue-800 text-sm">
                    🎥 Tutorial Videos
                  </a>
                  <a href="#docs" className="block text-blue-600 hover:text-blue-800 text-sm">
                    📚 Documentation
                  </a>
                  <a href="#status" className="block text-blue-600 hover:text-blue-800 text-sm">
                    🟢 System Status
                  </a>
                </div>
              </div>
            </div>

            {/* FAQ Content */}
            <div className="lg:col-span-3">
              <div className="bg-white rounded-lg shadow">
                <div className="p-6">
                  <h2 className="text-xl font-semibold text-gray-900 mb-6">
                    Frequently Asked Questions
                  </h2>
                  
                  {filteredFAQs.length === 0 ? (
                    <div className="text-center py-8">
                      <p className="text-gray-500">No questions found matching your search.</p>
                    </div>
                  ) : (
                    <div className="space-y-4">
                      {filteredFAQs.map((faq, index) => (
                        <div key={index} className="border border-gray-200 rounded-lg">
                          <button
                            onClick={() => setExpandedFAQ(expandedFAQ === index ? null : index)}
                            className="w-full text-left px-6 py-4 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-inset"
                          >
                            <div className="flex justify-between items-center">
                              <h3 className="text-lg font-medium text-gray-900">{faq.question}</h3>
                              <svg
                                className={`w-5 h-5 text-gray-500 transform transition-transform ${
                                  expandedFAQ === index ? 'rotate-180' : ''
                                }`}
                                fill="none"
                                stroke="currentColor"
                                viewBox="0 0 24 24"
                              >
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                              </svg>
                            </div>
                          </button>
                          {expandedFAQ === index && (
                            <div className="px-6 pb-4">
                              <p className="text-gray-700 leading-relaxed">{faq.answer}</p>
                            </div>
                          )}
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              </div>

              {/* Contact Support */}
              <div id="contact" className="bg-white rounded-lg shadow mt-6 p-6">
                <h2 className="text-xl font-semibold text-gray-900 mb-4">Contact Support</h2>
                <p className="text-gray-600 mb-4">
                  Can't find what you're looking for? Get in touch with our support team.
                </p>
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div>
                    <h3 className="font-medium text-gray-900 mb-2">Email Support</h3>
                    <p className="text-sm text-gray-600 mb-2">support@rockfallsystem.com</p>
                    <p className="text-xs text-gray-500">Response within 24 hours</p>
                  </div>
                  
                  <div>
                    <h3 className="font-medium text-gray-900 mb-2">Emergency Hotline</h3>
                    <p className="text-sm text-gray-600 mb-2">+1 (555) 123-4567</p>
                    <p className="text-xs text-gray-500">24/7 for critical issues</p>
                  </div>
                </div>

                <div className="mt-6">
                  <button className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-md text-sm font-medium transition-colors">
                    Open Support Ticket
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default HelpPage