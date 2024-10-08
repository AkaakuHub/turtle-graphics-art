"use client";

import React from 'react';
import { useSearchParams } from 'next/navigation'
import MainUI from '../_components/MainUI';
import Footer from '../_components/Footer';

const ImageProcessingApp: React.FC = () => {
  const searchParams = useSearchParams();
  const isTurtle = searchParams.has('turtle');

  return (
    <div className='window-wrapper'>
      <MainUI isTurtle={isTurtle} runMode={"server"} />
      <Footer isTurtle={isTurtle} />
    </div>
  );
};

export default ImageProcessingApp;