"use client";
import { useState, useEffect } from "react";
import axios from "axios";

// กำหนด type สำหรับ Item
interface Item {
  name: string;
  description: string;
  price: number;
}

// กำหนด type สำหรับ response จาก FastAPI
interface ApiResponse {
  message: string;
  item?: Item;
}

export default function Home() {
  const [name, setName] = useState<string>("");
  const [description, setDescription] = useState<string>("");
  const [price, setPrice] = useState<number>(0);
  const [message, setMessage] = useState<string>("");
  const [items, setItems] = useState<Item[]>([]);

  // ฟังก์ชันสำหรับส่ง POST request
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const response = await axios.post<ApiResponse>(
        "http://localhost:8000/items",
        {
          name,
          description,
          price,
        }
      );
      setMessage(response.data.message);
      setName("");
      setDescription("");
      fetchItems(); // อัพเดทรายการ items
    } catch (error: any) {
      setMessage("Error: " + error.message);
    }
  };

  // ฟังก์ชันสำหรับดึง items
  const fetchItems = async () => {
    try {
      const response = await axios.get<Item[]>("http://localhost:8000/items");
      setItems(response.data);
    } catch (error: any) {
      console.error("Error fetching items:", error);
    }
  };

  // เรียก fetchItems เมื่อหน้าโหลด
  useEffect(() => {
    fetchItems();
  }, []);

  return (
    <div className="max-w-2xl mx-auto p-6 bg-gray-50 min-h-screen">
      <h1 className="text-3xl font-bold text-gray-800 mb-6">เพิ่ม Item</h1>
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-700">
            Name
          </label>
          <input
            type="text"
            value={name}
            onChange={(e) => setName(e.target.value)}
            required
            className="mt-1 block w-full p-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700">
            Description
          </label>
          <input
            type="text"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            required
            className="mt-1 block w-full p-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700">
            Price
          </label>
          <input
            type="number"
            value={price}
            onChange={(e) => setPrice(Number(e.target.value))}
            required
            className="mt-1 block w-full p-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>
        <button
          type="submit"
          className="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 transition-colors"
        >
          เพิ่ม Item
        </button>
      </form>
      {message && (
        <p
          className={`mt-4 text-center ${
            message.includes("Error") ? "text-red-600" : "text-green-600"
          }`}
        >
          {message}
        </p>
      )}
      <h2 className="text-2xl font-semibold text-gray-800 mt-8 mb-4">
        รายการ Items
      </h2>
      <ul className="space-y-3">
        {items.map((item, index) => (
          <li
            key={index}
            className="p-3 bg-white border border-gray-200 rounded-md shadow-sm"
          >
            <span className="font-medium">{item.name}</span>: {item.description}
          </li>
        ))}
      </ul>
    </div>
  );
}
