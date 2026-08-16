from app.mcp_server import create_local_mcp_server

mcp = create_local_mcp_server()


if __name__ == "__main__":
    mcp.run()
