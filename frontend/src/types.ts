export type UserRole = "admin" | "seller" | "user";

export type User = {
  id: number;
  email: string;
  username: string;
  first_name?: string | null;
  last_name?: string | null;
  role: UserRole;
};

export type Category = {
  id: number;
  name: string;
};

export type Review = {
  id: number;
  user_id: number;
  product_id: number;
  rating: number;
  text: string;
  created_at: string;
};

export type Product = {
  id: number;
  name: string;
  description?: string | null;
  category_id: number;
  category: Category;
  price: string;
  rating: number;
  discount_percent: number;
  image_url?: string | null;
  is_active: boolean;
  seller_id?: number | null;
  reviews: Review[];
};

export type Promotion = {
  id: number;
  title: string;
  description?: string | null;
  discount_percent: number;
  starts_at: string;
  ends_at: string;
  is_active: boolean;
  product_id?: number | null;
  category_id?: number | null;
};

export type CartLine = {
  product: Product;
  quantity: number;
};

export type AuthResponse = {
  user: User;
  access_token: string;
  refresh_token: string;
  token_type: string;
};

export type ProductFilters = {
  categoryId?: number;
  minPrice?: number;
  maxPrice?: number;
  minRating?: number;
  search?: string;
  sellerId?: number;
};
