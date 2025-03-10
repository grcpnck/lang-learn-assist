// import type { NextApiRequest, NextApiResponse } from "next";

// export default async function handler(
//   req: NextApiRequest,
//   res: NextApiResponse
// ) {
//   if (req.method === "POST") {
//     const { message } = req.body;
//     const response = await fetch("http://localhost:3000/send", {
//       method: "POST",
//       headers: {
//         "Content-Type": "application/json",
//       },
//       body: JSON.stringify({ message }),
//     });
//     const data = await response.json();
//     // Here you would add your logic to process the message and generate a reply
//     const reply = data.reply;
//     res.status(200).json({ reply });
//   } else {
//     res.status(405).end(); // Method Not Allowed
//   }
// }
