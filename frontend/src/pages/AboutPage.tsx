/**
 * About Page
 * 
 * Project information, scientific references, and credits.
 */

import React from 'react';
import { motion } from 'framer-motion';
import {
  Info,
  ExternalLink,
  BookOpen,
  Award,
  Users,
  Shield,
} from 'lucide-react';

export const AboutPage: React.FC = () => {
  return (
    <div className="space-y-6 max-w-4xl mx-auto">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="glass rounded-2xl p-8 text-center"
      >
        <div className="w-20 h-20 mx-auto mb-6 rounded-2xl bg-gradient-to-br from-primary-500 to-accent-500 flex items-center justify-center shadow-lg shadow-primary-500/30">
          <Shield className="w-10 h-10 text-white" />
        </div>
        <h1 className="text-3xl font-bold text-white mb-2">
          G-Effects Safety Dashboard
        </h1>
        <p className="text-lg text-surface-400 mb-4">
          Aerospace Physiology Visualization Platform
        </p>
        <div className="inline-flex items-center gap-2 px-4 py-2 bg-surface-800/60 rounded-lg">
          <span className="text-sm text-surface-400">Based on</span>
          <span className="text-sm font-semibold text-primary-400">
            FAA CGEM v1.1.0.1
          </span>
        </div>
      </motion.div>

      {/* Description */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
        className="glass rounded-2xl p-6"
      >
        <h2 className="text-xl font-semibold text-white mb-4 flex items-center gap-2">
          <Info className="w-5 h-5 text-primary-400" />
          About This Project
        </h2>
        <div className="prose prose-invert max-w-none">
          <p className="text-surface-300 leading-relaxed">
            This dashboard provides interactive visualization and analysis tools for 
            aerospace physiology, specifically focused on G-induced loss of consciousness 
            (G-LOC) prediction and prevention. It is built upon the Combined G-Effects Model 
            (CGEM) developed by the FAA Civil Aerospace Medical Institute.
          </p>
          <p className="text-surface-300 leading-relaxed mt-4">
            The application supports training, safety analysis, and research in aerospace 
            medicine by providing publication-quality visualizations of G-force profiles, 
            physiological responses, and risk assessments.
          </p>
        </div>
      </motion.div>

      {/* Scientific References */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
        className="glass rounded-2xl p-6"
      >
        <h2 className="text-xl font-semibold text-white mb-4 flex items-center gap-2">
          <BookOpen className="w-5 h-5 text-accent-400" />
          Scientific References
        </h2>
        <div className="space-y-4">
          {[
            {
              authors: 'Copeland, K., & Whinnery, J. E.',
              year: '2023',
              title: 'Cerebral blood flow-based computer modeling of Gz-induced effects',
              source: 'DOT/FAA/AM-23/6, Office of Aerospace Medicine, FAA',
              doi: 'https://doi.org/10.21949/1524446',
            },
            {
              authors: 'Copeland, K.',
              year: '2021',
              title: 'CGEM User\'s Guide',
              source: 'DOT/FAA/AM-23/5, Office of Aerospace Medicine, FAA',
              doi: 'https://doi.org/10.21949/1524438',
            },
            {
              authors: 'Whinnery, T., & Forster, E. M.',
              year: '2015',
              title: 'Neurologic state transitions in the eye and brain: kinetics of loss and recovery of vision and consciousness',
              source: 'Visual Neuroscience, 32, E008',
              doi: 'https://doi.org/10.1017/S095252381500005X',
            },
            {
              authors: 'Tripp, L. D., et al.',
              year: '2009',
              title: 'Cerebral oxygen saturation and pilot performance during G-LOC',
              source: 'Human Factors, 51(6), 775-784',
              doi: 'https://doi.org/10.1177/0018720809359631',
            },
          ].map((ref, i) => (
            <a
              key={i}
              href={ref.doi}
              target="_blank"
              rel="noopener noreferrer"
              className="block p-4 bg-surface-800/50 rounded-xl hover:bg-surface-800 transition-colors group"
            >
              <div className="flex items-start justify-between gap-4">
                <div>
                  <p className="text-surface-200 group-hover:text-white font-medium">
                    {ref.authors} ({ref.year})
                  </p>
                  <p className="text-surface-400 text-sm mt-1">
                    {ref.title}
                  </p>
                  <p className="text-surface-500 text-xs mt-1">
                    {ref.source}
                  </p>
                </div>
                <ExternalLink className="w-4 h-4 text-surface-500 group-hover:text-primary-400 flex-shrink-0 mt-1" />
              </div>
            </a>
          ))}
        </div>
      </motion.div>

      {/* Attribution */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.3 }}
        className="glass rounded-2xl p-6"
      >
        <h2 className="text-xl font-semibold text-white mb-4 flex items-center gap-2">
          <Users className="w-5 h-5 text-warning-400" />
          Attribution
        </h2>
        <div className="space-y-4">
          <div className="p-4 bg-surface-800/50 rounded-xl">
            <p className="text-surface-200 font-medium">Original CGEM Model</p>
            <p className="text-surface-400 text-sm mt-1">
              FAA Civil Aerospace Medical Institute (CAMI), AAM-631
            </p>
            <p className="text-surface-500 text-xs mt-1">
              Foundational work by Kyle Copeland and collaborators
            </p>
          </div>
          <div className="p-4 bg-surface-800/50 rounded-xl">
            <p className="text-surface-200 font-medium">TypeScript Frontend Development</p>
            <p className="text-surface-400 text-sm mt-1">
              Based on the enhanced Streamlit application
            </p>
            <p className="text-surface-500 text-xs mt-1">
              Using React, ECharts, and TailwindCSS
            </p>
          </div>
        </div>
      </motion.div>

      {/* Disclaimer */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.4 }}
        className="glass-light rounded-xl p-4"
      >
        <h3 className="text-sm font-semibold text-warning-400 mb-2 flex items-center gap-2">
          <Award className="w-4 h-4" />
          Disclaimer
        </h3>
        <p className="text-xs text-surface-400 leading-relaxed">
          This toolkit is intended for research, education, and training support. 
          It does not substitute for operational aeromedical guidance or certification 
          processes. This project is not an official product of the FAA or the U.S. 
          Department of Defense. All views expressed are those of the contributors.
        </p>
      </motion.div>

      {/* Footer */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.5 }}
        className="text-center text-surface-500 text-sm py-4"
      >
        <p>
          © 2024 G-Effects Safety Dashboard. Open source under MIT License.
        </p>
      </motion.div>
    </div>
  );
};

export default AboutPage;
