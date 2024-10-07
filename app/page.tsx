"use client";

import React, { useState, ChangeEvent } from 'react';
import { TurtleJsonType } from './types';
import './page.css';

import generateTurtleCommands from '@/lib/generateTurtleCommands';

interface ApiResponse {
  dilatedBase64: string;
}

const ImageProcessingApp: React.FC = () => {
  const [fileName, setFileName] = useState<string>('');
  const [selectedImage, setSelectedImage] = useState<string | null>(null);
  const [processedImage, setProcessedImage] = useState<string | null>(null);
  const [turtleJson, setTurtleJson] = useState<string | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const [isGeneratingJson, setIsGeneratingJson] = useState<boolean>(false);

  const handleFileChange = (event: ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      setFileName(file.name);
      const reader = new FileReader();
      reader.onloadend = () => {
        setSelectedImage(reader.result as string);
      };
      reader.readAsDataURL(file);
    }
  };

  const handleSubmit = async () => {
    if (!selectedImage || !fileName) return;

    setLoading(true);
    setError(null);
    setProcessedImage(null);
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 60000);

    try {
      const response = await fetch('/api/run', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          imageBase64: selectedImage.split(',')[1],
        }),
        signal: controller.signal,
      });

      clearTimeout(timeoutId);

      if (response.ok) {
        const data: ApiResponse = await response.json();
        const dilatedBase64 = data.dilatedBase64;
        setProcessedImage(`data:image/png;base64,${dilatedBase64}`);
      } else {
        console.error('APIエラー:', response.statusText);
        setError(`APIエラー:, ${response.statusText}`);
      }
    } catch (error) {
      const err = error as Error;
      if (err.name === 'AbortError') {
        console.error('タイムアウトエラー: サーバーからの応答がありませんでした。');
        setError('タイムアウトエラー: サーバーからの応答がありませんでした。');
      } else {
        console.error(`エラーが発生しました: ${err.message}`);
        setError(`エラーが発生しました: ${err.message}`);
      }
    } finally {
      setLoading(false);
    }
  };

  const handleDownload = () => {
    if (turtleJson) {
      const blob = new Blob([turtleJson], { type: 'application/json' });
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = 'turtle.json';
      link.click();
    }
  };

  const handleGenerateTurtleJson = async () => {
    if (!processedImage) {
      setError('画像が処理されていません');
      return;
    }
    setIsGeneratingJson(true);
    try {
      setTurtleJson(null);
      const data = await generateTurtleCommands({ imageBase64: processedImage.split(',')[1] });
      try {
        const trueData: TurtleJsonType = data;
        setTurtleJson(JSON.stringify(trueData, null, 0));
      } catch (error) {
        console.error(`型が一致しません: ${error}`);
        setError(`型が一致しません: ${error}`);
      }
    } catch (error) {
      console.error(`エラーが発生しました: ${error}`);
      setError(`エラーが発生しました: ${error}`);
    }
    setIsGeneratingJson(false);
  }

  return (
    <div className="window-container">
      <div className="window-title">イラストの線画抽出アプリ&#040;サーバー版&#041;</div>
      <div>Vercel上でのOpenCVデモ</div>
      <div className="input-section">
        <input
          className="input-file"
          type="file"
          accept="image/*"
          onChange={handleFileChange}
        />
        <button className="submit-button" onClick={handleSubmit} disabled={loading || !selectedImage}>
          開始
        </button>
      </div>
      {loading && <p className="loading-text">処理中...</p>}
      {error && <p className="error-text">{error}</p>}
      {selectedImage && (
        <div className="image-section">
          <h2 className="section-title">選択した画像:</h2>
          <img className="image-display" src={selectedImage} alt="Selected" />
        </div>
      )}
      {processedImage && (
        <div className="image-section">
          <h2 className="section-title">処理された画像:</h2>
          <img className="image-display" src={processedImage} alt="Processed" />
        </div>
      )}
      {
        processedImage && (
          <div>
            <button className='submit-button'
              disabled={isGeneratingJson}
              onClick={async () => {
                await handleGenerateTurtleJson();
              }}>jsonを生成&#040;ローカル&#041;</button>
          </div>
        )
      }
      {turtleJson && (
        <div className="download-section">
          <button className="download-button" onClick={handleDownload}>
            turtle.jsonをダウンロード
          </button>
        </div>
      )}
    </div>
  );
};

export default ImageProcessingApp;