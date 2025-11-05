/**
 * Footer Component
 * 
 * Reusable footer with copyright and attribution
 */
export default function Footer() {
  return (
    <footer className="bg-gray-800 border-t border-gray-700 mt-16">
      <div className="container mx-auto px-4 py-6 text-center text-gray-400 text-sm">
        <p>
          Data sourced from{' '}
          <a
            href="https://arcraiders.wiki/"
            target="_blank"
            rel="noopener noreferrer"
            className="text-blue-400 hover:text-blue-300"
          >
            arcraiders.wiki
          </a>
        </p>
        <p className="mt-2">
          No user accounts required • All progress saved locally in your browser
        </p>
        <div className="mt-4 pt-4 border-t border-gray-700 max-w-3xl mx-auto">
          <p className="text-xs leading-relaxed">
            All game content and materials are copyright of Embark Studios AB.
            ARC RAIDERS and EMBARK trademarks and logos are trademarks or registered trademarks of Embark Studios AB.
            Other content is available under Creative Commons Attribution-ShareAlike unless otherwise noted.
          </p>
        </div>
      </div>
    </footer>
  );
}
