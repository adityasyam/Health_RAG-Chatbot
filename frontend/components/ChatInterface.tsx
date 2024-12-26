import React, { useState, useRef } from "react";
import axios from "axios";
import { Button } from "@/components/ui/button";

interface Message {
  type: "user" | "bot";
  content: string;
}

const ChatInterface = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [isRecording, setIsRecording] = useState(false);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const fetchResponse = async (query: string) => {
    try {
      setLoading(true);
      setMessages((prev) => [...prev, { type: "user", content: query }]);

      const response = await axios.post("http://localhost:8000/chat", {
        user_query: query
      });

      setMessages((prev) => [...prev, { type: "bot", content: response.data }]);
    } catch (error) {
      console.error("Error fetching response:", error);
      setMessages((prev) => [...prev, {
        type: "bot",
        content: "Sorry, there was an error processing your request."
      }]);
    } finally {
      setLoading(false);
    }
  };

  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    if (file.type !== 'text/plain' && file.type !== 'application/pdf') {
      setMessages((prev) => [
        ...prev,
        {
          type: "bot",
          content: "Please upload a valid .txt or .pdf file with the patient record.",
        },
      ]);
      return;
    }

    try {
      setLoading(true);
      const formData = new FormData();
      formData.append('file', file);

      const response = await axios.post("http://localhost:8000/upload-record", formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      setMessages((prev) => [...prev, { type: "bot", content: response.data }]);
    } catch (error) {
      console.error("Error uploading file:", error);
      setMessages((prev) => [
        ...prev,
        {
          type: "bot",
          content: "There was an error uploading the patient record. Please try again.",
        },
      ]);
    } finally {
      setLoading(false);
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    }
  };

  const handleUploadClick = () => {
    fileInputRef.current?.click();
  };

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      mediaRecorderRef.current = new MediaRecorder(stream);
      audioChunksRef.current = [];

      mediaRecorderRef.current.ondataavailable = (event) => {
        audioChunksRef.current.push(event.data);
      };

      mediaRecorderRef.current.start();
      setIsRecording(true);
    } catch (error) {
      console.error("Error starting recording:", error);
      setMessages((prev) => [...prev, {
        type: "bot",
        content: "Could not start recording. Please check your microphone permissions."
      }]);
    }
  };

  const stopRecording = async () => {
    if (!mediaRecorderRef.current) return;

    const mediaRecorder = mediaRecorderRef.current;
    return new Promise<void>((resolve) => {
      mediaRecorder.onstop = async () => {
        const audioBlob = new Blob(audioChunksRef.current, { type: "audio/wav" });
        const formData = new FormData();
        formData.append("audio_file", audioBlob, "recording.wav");

        try {
          setLoading(true);
          const response = await axios.post("http://localhost:8000/voice", formData, {
            responseType: "blob",
          });

          const audioUrl = URL.createObjectURL(response.data);
          const audio = new Audio(audioUrl);
          audio.play();
        } catch (error) {
          console.error("Error getting voice response:", error);
          setMessages((prev) => [...prev, {
            type: "bot",
            content: "There was an error processing your voice recording."
          }]);
        } finally {
          setLoading(false);
        }
        resolve();
      };

      mediaRecorder.stop();
      mediaRecorder.stream.getTracks().forEach((track) => track.stop());
      setIsRecording(false);
    });
  };

  const handleSend = () => {
    if (!input.trim()) return;
    fetchResponse(input);
    setInput("");
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="flex flex-col w-[800px] h-[600px] bg-gray-100 rounded-lg shadow-md">
      <div className="flex-grow overflow-y-auto p-4 space-y-4">
        {messages.map((message, index) => (
          <div
            key={index}
            className={`flex ${message.type === "user" ? "justify-end" : "justify-start"}`}
          >
            <div
              className={`${message.type === "user"
                ? "bg-blue-500 text-white"
                : "bg-white"
                } rounded-lg p-3 max-w-[90%] shadow`}
            >
              <p className="whitespace-pre-wrap">{message.content}</p>
            </div>
          </div>
        ))}
      </div>

      <div className="flex items-center border-t border-gray-300 p-4 bg-white rounded-b-lg">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder="Type your message..."
          className="flex-grow p-2 border border-gray-300 rounded-lg focus:outline-none focus:ring focus:ring-blue-300"
          disabled={loading}
        />
        <input
          type="file"
          ref={fileInputRef}
          onChange={handleFileUpload}
          className="hidden"
          accept=".txt, .pdf"
        />
        <Button
          onClick={handleSend}
          disabled={loading || !input.trim()}
          className="ml-2"
        >
          {loading ? "Sending..." : "Send"}
        </Button>
        <Button
          onClick={isRecording ? stopRecording : startRecording}
          variant={isRecording ? "destructive" : "secondary"}
          disabled={loading}
          className="ml-2"
        >
          {isRecording ? "Stop Recording" : "Start Recording"}
        </Button>
        <Button
          onClick={handleUploadClick}
          variant="outline"
          disabled={loading}
          className="ml-2"
        >
          Upload Record
        </Button>
      </div>
    </div>
  );
};

export default ChatInterface;