export const customers = [
  {
    id: "M001",
    name: "John Doe",
    email: "john.doe@gmail.com",
    phone: "9876543210",
    dob: "10 May 2000",
    address: "12 MG Street",
    qualityScore: 96,

    lineage: {
      name: "Core Banking",
      email: "Credit Card",
      phone: "Core Banking",
      dob: "Core Banking",
      address: "Core Banking",
    },

    products: [
      {
        id: "A001",
        type: "Savings Account",
        source: "Core Banking",
        number: "XXXX 4521",
        balance: "₹82,450",
        status: "Active",
      },
      {
        id: "A002",
        type: "Current Account",
        source: "Core Banking",
        number: "XXXX 7812",
        balance: "₹35,200",
        status: "Active",
      },
      {
        id: "CC001",
        type: "Credit Card",
        source: "Credit Card",
        number: "XXXX XXXX XXXX 4821",
        balance: "₹12,400",
        status: "Active",
      },
      {
        id: "L001",
        type: "Personal Loan",
        source: "Loan System",
        number: "LN-001",
        balance: "₹8,00,000",
        status: "Active",
      },
    ],

    transactions: [
      {
        id: "TX001",
        date: "24 Sep 2026",
        amount: "₹5,000",
        type: "Debit",
        product: "Savings Account",
      },
      {
        id: "TX002",
        date: "21 Sep 2026",
        amount: "₹2,000",
        type: "Credit",
        product: "Credit Card",
      },
      {
        id: "TX003",
        date: "18 Sep 2026",
        amount: "₹8,500",
        type: "Debit",
        product: "Savings Account",
      },
      {
        id: "TX004",
        date: "15 Sep 2026",
        amount: "₹15,000",
        type: "Debit",
        product: "Current Account",
      },
    ],
  },

  {
    id: "M002",
    name: "Priya Shah",
    email: "priya.shah@gmail.com",
    phone: "9123456789",
    dob: "18 March 2001",
    address: "45 MG Road",
    qualityScore: 92,

    lineage: {
      name: "Core Banking",
      email: "Credit Card",
      phone: "Core Banking",
      dob: "Core Banking",
      address: "Loan System",
    },

    products: [
      {
        id: "A003",
        type: "Savings Account",
        source: "Core Banking",
        number: "XXXX 2391",
        balance: "₹54,200",
        status: "Active",
      },
      {
        id: "CC002",
        type: "Credit Card",
        source: "Credit Card",
        number: "XXXX XXXX XXXX 8212",
        balance: "₹4,500",
        status: "Active",
      },
    ],

    transactions: [
      {
        id: "TX005",
        date: "23 Sep 2026",
        amount: "₹3,500",
        type: "Debit",
        product: "Savings Account",
      },
      {
        id: "TX006",
        date: "20 Sep 2026",
        amount: "₹1,200",
        type: "Credit",
        product: "Credit Card",
      },
    ],
  },

  {
    id: "M003",
    name: "Rahul Kumar",
    email: "rahul.kumar@gmail.com",
    phone: "9988776655",
    dob: "7 July 1999",
    address: "22 Residency Road",
    qualityScore: 88,

    lineage: {
      name: "Credit Card",
      email: "Credit Card",
      phone: "Core Banking",
      dob: "Core Banking",
      address: "Core Banking",
    },

    products: [
      {
        id: "A004",
        type: "Savings Account",
        source: "Core Banking",
        number: "XXXX 1142",
        balance: "₹1,20,500",
        status: "Active",
      },
      {
        id: "CC003",
        type: "Credit Card",
        source: "Credit Card",
        number: "XXXX XXXX XXXX 3345",
        balance: "₹18,200",
        status: "Active",
      },
      {
        id: "L002",
        type: "Home Loan",
        source: "Loan System",
        number: "LN-002",
        balance: "₹24,50,000",
        status: "Active",
      },
    ],

    transactions: [
      {
        id: "TX007",
        date: "24 Sep 2026",
        amount: "₹12,000",
        type: "Debit",
        product: "Savings Account",
      },
      {
        id: "TX008",
        date: "19 Sep 2026",
        amount: "₹45,000",
        type: "Debit",
        product: "Credit Card",
      },
    ],
  },

  {
    id: "M004",
    name: "Ananya Rao",
    email: "ananya.rao@gmail.com",
    phone: "9012345678",
    dob: "12 January 2002",
    address: "18 Indiranagar",
    qualityScore: 100,

    lineage: {
      name: "Core Banking",
      email: "Credit Card",
      phone: "Core Banking",
      dob: "Core Banking",
      address: "Core Banking",
    },

    products: [
      {
        id: "A005",
        type: "Savings Account",
        source: "Core Banking",
        number: "XXXX 5521",
        balance: "₹67,800",
        status: "Active",
      },
    ],

    transactions: [
      {
        id: "TX009",
        date: "25 Sep 2026",
        amount: "₹2,500",
        type: "Debit",
        product: "Savings Account",
      },
    ],
  },

  {
    id: "M005",
    name: "Arjun Mehta",
    email: "arjun.mehta@gmail.com",
    phone: "9345678123",
    dob: "29 November 1998",
    address: "77 Koramangala",
    qualityScore: 84,

    lineage: {
      name: "Core Banking",
      email: "Core Banking",
      phone: "Core Banking",
      dob: "Loan System",
      address: "Credit Card",
    },

    products: [
      {
        id: "A006",
        type: "Current Account",
        source: "Core Banking",
        number: "XXXX 9182",
        balance: "₹2,40,000",
        status: "Active",
      },
      {
        id: "CC004",
        type: "Credit Card",
        source: "Credit Card",
        number: "XXXX XXXX XXXX 7291",
        balance: "₹27,800",
        status: "Active",
      },
    ],

    transactions: [
      {
        id: "TX010",
        date: "22 Sep 2026",
        amount: "₹18,000",
        type: "Debit",
        product: "Current Account",
      },
      {
        id: "TX011",
        date: "17 Sep 2026",
        amount: "₹6,500",
        type: "Credit",
        product: "Credit Card",
      },
    ],
  },

  {
    id: "M006",
    name: "Sneha Iyer",
    email: "sneha.iyer@gmail.com",
    phone: "9765432108",
    dob: "4 February 2000",
    address: "31 Jayanagar",
    qualityScore: 94,

    lineage: {
      name: "Core Banking",
      email: "Credit Card",
      phone: "Core Banking",
      dob: "Core Banking",
      address: "Core Banking",
    },

    products: [
      {
        id: "A007",
        type: "Savings Account",
        source: "Core Banking",
        number: "XXXX 6734",
        balance: "₹91,300",
        status: "Active",
      },
      {
        id: "CC005",
        type: "Credit Card",
        source: "Credit Card",
        number: "XXXX XXXX XXXX 1982",
        balance: "₹7,800",
        status: "Active",
      },
      {
        id: "L003",
        type: "Education Loan",
        source: "Loan System",
        number: "LN-003",
        balance: "₹3,20,000",
        status: "Active",
      },
    ],

    transactions: [
      {
        id: "TX012",
        date: "24 Sep 2026",
        amount: "₹4,200",
        type: "Debit",
        product: "Savings Account",
      },
      {
        id: "TX013",
        date: "16 Sep 2026",
        amount: "₹2,800",
        type: "Debit",
        product: "Credit Card",
      },
    ],
  },

  {
    id: "M007",
    name: "Vikram Patel",
    email: "vikram.patel@gmail.com",
    phone: "8899001122",
    dob: "16 August 1997",
    address: "9 Whitefield Main Road",
    qualityScore: 79,

    lineage: {
      name: "Credit Card",
      email: "Credit Card",
      phone: "Core Banking",
      dob: "Core Banking",
      address: "Loan System",
    },

    products: [
      {
        id: "A008",
        type: "Savings Account",
        source: "Core Banking",
        number: "XXXX 3456",
        balance: "₹45,600",
        status: "Active",
      },
      {
        id: "L004",
        type: "Personal Loan",
        source: "Loan System",
        number: "LN-004",
        balance: "₹4,80,000",
        status: "Active",
      },
    ],

    transactions: [
      {
        id: "TX014",
        date: "20 Sep 2026",
        amount: "₹7,500",
        type: "Debit",
        product: "Savings Account",
      },
    ],
  },

  {
    id: "M008",
    name: "Neha Sharma",
    email: "neha.sharma@gmail.com",
    phone: "9876123450",
    dob: "25 April 2001",
    address: "14 HSR Layout",
    qualityScore: 91,

    lineage: {
      name: "Core Banking",
      email: "Credit Card",
      phone: "Core Banking",
      dob: "Core Banking",
      address: "Core Banking",
    },

    products: [
      {
        id: "A009",
        type: "Savings Account",
        source: "Core Banking",
        number: "XXXX 8234",
        balance: "₹73,900",
        status: "Active",
      },
      {
        id: "CC006",
        type: "Credit Card",
        source: "Credit Card",
        number: "XXXX XXXX XXXX 4512",
        balance: "₹9,200",
        status: "Active",
      },
    ],

    transactions: [
      {
        id: "TX015",
        date: "25 Sep 2026",
        amount: "₹3,200",
        type: "Debit",
        product: "Savings Account",
      },
      {
        id: "TX016",
        date: "22 Sep 2026",
        amount: "₹1,800",
        type: "Credit",
        product: "Credit Card",
      },
    ],
  },

  {
    id: "M009",
    name: "Karthik Reddy",
    email: "karthik.reddy@gmail.com",
    phone: "9001122334",
    dob: "3 December 1996",
    address: "56 Marathahalli",
    qualityScore: 87,

    lineage: {
      name: "Core Banking",
      email: "Core Banking",
      phone: "Core Banking",
      dob: "Core Banking",
      address: "Credit Card",
    },

    products: [
      {
        id: "A010",
        type: "Current Account",
        source: "Core Banking",
        number: "XXXX 5678",
        balance: "₹3,10,000",
        status: "Active",
      },
      {
        id: "CC007",
        type: "Credit Card",
        source: "Credit Card",
        number: "XXXX XXXX XXXX 6754",
        balance: "₹22,600",
        status: "Active",
      },
      {
        id: "L005",
        type: "Business Loan",
        source: "Loan System",
        number: "LN-005",
        balance: "₹12,00,000",
        status: "Active",
      },
    ],

    transactions: [
      {
        id: "TX017",
        date: "24 Sep 2026",
        amount: "₹25,000",
        type: "Debit",
        product: "Current Account",
      },
      {
        id: "TX018",
        date: "19 Sep 2026",
        amount: "₹11,500",
        type: "Debit",
        product: "Credit Card",
      },
    ],
  },

  {
    id: "M010",
    name: "Meera Nair",
    email: "meera.nair@gmail.com",
    phone: "9112233445",
    dob: "9 September 1999",
    address: "28 Malleshwaram",
    qualityScore: 97,

    lineage: {
      name: "Core Banking",
      email: "Credit Card",
      phone: "Core Banking",
      dob: "Core Banking",
      address: "Core Banking",
    },

    products: [
      {
        id: "A011",
        type: "Savings Account",
        source: "Core Banking",
        number: "XXXX 9012",
        balance: "₹1,05,400",
        status: "Active",
      },
      {
        id: "CC008",
        type: "Credit Card",
        source: "Credit Card",
        number: "XXXX XXXX XXXX 3421",
        balance: "₹5,600",
        status: "Active",
      },
    ],

    transactions: [
      {
        id: "TX019",
        date: "25 Sep 2026",
        amount: "₹6,000",
        type: "Debit",
        product: "Savings Account",
      },
      {
        id: "TX020",
        date: "23 Sep 2026",
        amount: "₹2,500",
        type: "Credit",
        product: "Credit Card",
      },
    ],
  },
];

export function getCustomerById(id) {
  return customers.find((customer) => customer.id === id);
}