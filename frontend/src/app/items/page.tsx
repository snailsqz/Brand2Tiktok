"use client";
import { useState, useEffect } from "react";
import axios from "axios";
import Link from "next/link";
import { useRouter } from "next/navigation";

interface Item {
  id: number;
  name: string;
  price: number;
}

export default function ItemsPage() {
  const [items, setItems] = useState<Item[]>([]);
  const router = useRouter();

  const fetchItems = async () => {
    try {
      const response = await axios.get<Item[]>("http://127.0.0.1:8000/items/");
      setItems(response.data);
    } catch (error) {
      console.error("Failed to fetch items:", error);
    }
  };

  useEffect(() => {
    fetchItems();
  }, []);

  const handleDelete = async (id: number) => {
    try {
      await axios.delete(`http://127.0.0.1:8000/items/${id}`);
      // รีโหลดหน้าหลังจากลบ
      router.refresh();
    } catch (error) {
      console.error("Failed to delete item:", error);
    }
  };

  return (
    <main>
      <h1>Item List</h1>
      <Link href="/items/new">
        <button>Create New Item</button>
      </Link>
      <ul>
        {items.map((item) => (
          <li key={item.id}>
            {item.name} - ${item.price}
            <Link href={`/items/${item.id}/edit`}>
              <button>Edit</button>
            </Link>
            <button onClick={() => handleDelete(item.id)}>Delete</button>
          </li>
        ))}
      </ul>
    </main>
  );
}
