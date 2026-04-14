const Footer = () => {
  return (
    <footer className="w-full bg-sky-300 text-sky-800 text-center py-4 mt-auto border-t border-sky-100">
      <p className="text-sm">
        &copy; {new Date().getFullYear()} Document Hub. All rights reserved.
      </p>
    </footer>
  );
};
export default Footer;
